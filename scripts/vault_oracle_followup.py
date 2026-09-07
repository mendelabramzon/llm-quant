#!/usr/bin/env python3
"""Reconstruct oracle dependencies and rank accounting anomalies, without trading."""
import argparse
import hashlib
import json
from pathlib import Path
from non_mev_screen import Evidence,ROOT,calldata,words,addr,string
from vault_oracle_scan import multicall,scalar,save


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'research/2026-09-07/vault_oracles')
    p.add_argument('--offline',action='store_true');a=p.parse_args();e=Evidence(a.out,a.offline)
    h=json.loads((a.out/'snapshot.json').read_text());block=h['number'];now=h['timestamp']
    m=json.loads((a.out/'markets.json').read_text());v=json.loads((a.out/'vaults.json').read_text())
    oracles=m['oracles']
    address_fields=['BASE_VAULT','QUOTE_VAULT','BASE_FEED_1','BASE_FEED_2','QUOTE_FEED_1','QUOTE_FEED_2']
    def valid_v2(o):
        return (o.get('SCALE_FACTOR') is not None and o['SCALE_FACTOR']>0 and
                all(o.get(k) is not None and 0<=o[k]<2**160 for k in address_fields) and
                all(o.get(k+'_CONVERSION_SAMPLE') is not None and o[k+'_CONVERSION_SAMPLE']>0 and
                    (o[k]!=0 or o[k+'_CONVERSION_SAMPLE']==1) for k in ['BASE_VAULT','QUOTE_VAULT']))
    standard={a:o for a,o in oracles.items() if valid_v2(o)}
    feeds=sorted({addr(o[k]) for o in standard.values() for k in
        ['BASE_FEED_1','BASE_FEED_2','QUOTE_FEED_1','QUOTE_FEED_2'] if o.get(k)})
    res=multicall(e,[(f,calldata(sig)) for f in feeds for sig in ['latestRoundData()','decimals()','description()']],block)
    feed_data={}
    for i,f in enumerate(feeds):
        rd,dc,ds=res[i*3:i*3+3];row={'raw_round_data':rd,'decimals':scalar(dc)}
        try:row['description']=string(ds) if ds else None
        except (UnicodeError,ValueError,IndexError):row['description']=None
        if rd and len(rd)==322:
            w=words(rd);answer=w[1] if w[1]<2**255 else w[1]-2**256
            row.update({'round_id':w[0],'answer':answer,'updated_at':w[3],
                        'age_seconds':now-w[3] if w[3] else None,
                        'timestamp_status':('absent_or_adapter_zero' if not w[3] else
                                            'future' if w[3]>now else 'positive_timestamp'),
                        'answered_in_round':w[4]})
        feed_data[f]=row
    samples=sorted({(addr(o[k]),o[k+'_CONVERSION_SAMPLE']) for o in standard.values()
                    for k in ['BASE_VAULT','QUOTE_VAULT'] if o.get(k) and o.get(k+'_CONVERSION_SAMPLE')})
    res=multicall(e,[(vault,calldata('convertToAssets(uint256)',amount*scale)) for vault,amount in samples for scale in [1,10,100]],block)
    sample_data={}
    for i,(vault,amount) in enumerate(samples):
        values=[scalar(x) for x in res[i*3:i*3+3]]
        sample_data[vault+':'+str(amount)]={'vault':vault,'sample':amount,'assets_at_1_10_100x':values,
            'scaling_deviation_raw':[values[i]-values[0]*scale if values[i] is not None and values[0] is not None else None
                                     for i,scale in enumerate([1,10,100])]}
    oracle_checks=[]
    for address,o in oracles.items():
        row={'address':address,'quoted_price':o['price'],'configuration':o,
             'affected_markets':[r['id'] for r in m['markets'] if r['oracle']==address]}
        row['valid_v2_getter_configuration']=valid_v2(o)
        if valid_v2(o):
            def side(kind):
                vault=o[kind+'_VAULT'];val=1
                if vault:
                    val=sample_data[addr(vault)+':'+str(o[kind+'_VAULT_CONVERSION_SAMPLE'])]['assets_at_1_10_100x'][0]
                if val is None:return None
                for key in [kind+'_FEED_1',kind+'_FEED_2']:
                    if o[key]:
                        answer=feed_data[addr(o[key])].get('answer')
                        if answer is None or answer<=0:return None
                        val*=answer
                return val
            base,quote=side('BASE'),side('QUOTE')
            if base is not None and quote:
                rebuilt=o['SCALE_FACTOR']*base//quote
                row['reconstructed_price']=rebuilt;row['exact_match']=rebuilt==o['price']
            row['constant_no_feed_no_vault']=all(o[k]==0 for k in
                ['BASE_VAULT','QUOTE_VAULT','BASE_FEED_1','BASE_FEED_2','QUOTE_FEED_1','QUOTE_FEED_2'])
            row['zero_feed_slots']=[k for k in ['BASE_FEED_1','BASE_FEED_2','QUOTE_FEED_1','QUOTE_FEED_2'] if not o[k]]
        oracle_checks.append(row)
    # Deposits are probed with no allowance or funded wallet: maxDeposit > 0 does
    # not establish unrestricted execution, and maxWithdraw(probe)==0 is expected.
    unlock=[];gaps=[]
    for r in v['vaults']:
        if r['profitMaxUnlockTime'] and r['self_held_shares'] and r['totalSupply']:
            remaining=max(0,(r['fullProfitUnlockDate'] or 0)-now)
            fraction=r['self_held_shares']/r['totalSupply']
            unlock.append({'address':r['address'],'symbol':r['metadata']['symbol'],
                'asset':r['asset'],'asset_symbol':r['asset_metadata']['symbol'],'assets_units':r.get('assets_units'),
                'self_held_fraction':fraction,'remaining_seconds':remaining,
                'undiluted_return_if_all_remaining_self_shares_burn':fraction/(1-fraction) if fraction<1 else None,
                'maxDeposit_probe':r['maxDeposit_probe'],'idle_units':r.get('idle_units')})
        if r['totalAssets'] and r['idle_assets'] and r['idle_assets']>r['totalAssets']:
            gaps.append({'address':r['address'],'symbol':r['metadata']['symbol'],'asset':r['asset'],
                'asset_symbol':r['asset_metadata']['symbol'],'assets_units':r.get('assets_units'),
                'idle_units':r.get('idle_units'),'excess_raw':r['idle_assets']-r['totalAssets'],
                'excess_fraction':r['idle_assets']/r['totalAssets']-1})
    save(a.out,'oracle_checks.json',{'snapshot':h,'feed_dependencies':feed_data,'vault_samples':sample_data,'oracles':oracle_checks})
    save(a.out,'accounting_candidates.json',{'unlock':sorted(unlock,key=lambda r:-r['self_held_fraction']),
        'idle_above_accounted':sorted(gaps,key=lambda r:-r['excess_fraction'])})
    save(a.out,'sha256.json',{str(p.relative_to(a.out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((a.out/'raw').glob('*.json'))})
    print(json.dumps({'feeds':len(feeds),'vault_conversion_samples':len(samples),'oracles':len(oracle_checks),
        'exact_reconstructions':sum(r.get('exact_match',False) for r in oracle_checks),
        'mismatches':sum(r.get('exact_match') is False for r in oracle_checks),
        'feeds_older_than_24h':[{'feed':f,'description':r.get('description'),'age_hours':r['age_seconds']/3600}
                              for f,r in feed_data.items() if (r.get('age_seconds') or 0)>86400],
        'zero_timestamp_adapters':sum(r.get('timestamp_status')=='absent_or_adapter_zero' for r in feed_data.values()),
        'unlock_candidates':len(unlock),'idle_above_accounted':len(gaps)},indent=2))


if __name__=='__main__':main()
