#!/usr/bin/env python3
"""Read-only discovery of active Ethereum vaults and Morpho oracle dependencies.

Scans the saved full-day and live logs, then inspects the deployed interfaces at a
fixed finalized block. Event signatures alone never establish protocol identity.
"""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path

from eth_abi import encode, decode
from non_mev_screen import Evidence, ROOT, calldata, digest, words, addr, string

MORPHO='0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
MULTICALL='0xca11bde05977b3631167028862be2a173976ca11'
OUT=ROOT/'research/2026-09-06/vault_oracles'
VAULT_TOPICS={'0x'+digest(s):k for k,s in {
    'deposit':'Deposit(address,address,uint256,uint256)',
    'withdraw':'Withdraw(address,address,address,uint256,uint256)'}.items()}
MARKET_TOPICS={'0x'+digest(s) for s in [
    'Supply(bytes32,address,address,uint256,uint256)',
    'Withdraw(bytes32,address,address,address,uint256,uint256)',
    'Borrow(bytes32,address,address,address,uint256,uint256)',
    'Repay(bytes32,address,address,uint256,uint256)',
    'SupplyCollateral(bytes32,address,address,uint256)',
    'WithdrawCollateral(bytes32,address,address,address,uint256)',
    'Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)']}


def save(out,name,data):
    (out/name).write_text(json.dumps(data,indent=2)+'\n')


def discover(out,block):
    path=out/'discovery.json'
    if path.exists():
        return json.loads(path.read_text())
    files={}
    for dataset in ['research/2026-09-05/eth_day','research/2026-09-06/live']:
        for p in (ROOT/dataset/'raw/logs').glob('*.json.gz'):
            n=int(p.name.split('.')[0])
            if n<=block:files[n]=p
    vaults={};markets=collections.Counter();log_count=0
    for index,(n,p) in enumerate(sorted(files.items())):
        logs=json.loads(gzip.decompress(p.read_bytes()));log_count+=len(logs)
        for l in logs:
            topics=l['topics']
            if not topics:continue
            t=topics[0]
            if l['address']==MORPHO and t in MARKET_TOPICS and len(topics)>1:
                markets[topics[1]]+=1
            if t not in VAULT_TOPICS or len(l['data'])!=130:
                continue
            r=vaults.setdefault(l['address'],{'events':0,'deposit_events':0,'withdraw_events':0,
                'deposited_assets_raw':0,'withdrawn_assets_raw':0,'first_block':n,'last_block':n,'examples':[]})
            kind=VAULT_TOPICS[t];w=words(l['data']);r['events']+=1;r[kind+'_events']+=1
            r['deposited_assets_raw' if kind=='deposit' else 'withdrawn_assets_raw']+=w[0]
            r['last_block']=n
            if len(r['examples'])<3:r['examples'].append({'block':n,'tx':l['transactionHash'],'kind':kind})
        if index and index%2000==0:print('discovery blocks',index,'vault candidates',len(vaults),flush=True)
    result={'scope':{'first_block':min(files),'last_block':max(files),'block_files':len(files),'logs':log_count,
            'datasets':['research/2026-09-05/eth_day','research/2026-09-06/live'],
            'continuous_interval':False,'finalized_state_block':block},
            'vault_candidates':dict(sorted(vaults.items(),key=lambda x:-x[1]['events'])),
            'morpho_market_ids':dict(markets.most_common())}
    save(out,'discovery.json',result)
    return result


def multicall(e,items,block,size=60):
    """Only locally simulated getters. Failure and empty return are retained as None."""
    result=[]
    for start in range(0,len(items),size):
        chunk=items[start:start+size]
        data='0x'+digest('aggregate3((address,bool,bytes)[])')[:8]+encode(['(address,bool,bytes)[]'],
            [[(a,True,bytes.fromhex(d[2:])) for a,d in chunk]]).hex()
        raw=e.get('eth_call',[{'to':MULTICALL,'data':data,'gas':hex(25_000_000)},hex(block)])
        decoded=decode(['(bool,bytes)[]'],bytes.fromhex(raw[2:]))[0]
        assert len(decoded)==len(chunk)
        result.extend('0x'+b.hex() if ok and b else None for ok,b in decoded)
    return result


def scalar(raw):
    return words(raw)[0] if raw and len(raw)==66 else None


def metadata(e,addresses,block):
    keys=['symbol','name','decimals']
    results=multicall(e,[(a,calldata(k+'()')) for a in addresses for k in keys],block)
    out={}
    for i,a in enumerate(addresses):
        row={}
        for k,r in zip(keys,results[i*3:i*3+3]):
            try:row[k]=scalar(r) if k=='decimals' else string(r) if r else None
            except (ValueError,UnicodeError,IndexError):row[k]=None
        out[a]=row
    return out


def inspect_vaults(e,discovery,block):
    candidates=sorted(discovery['vault_candidates'])
    fields=['asset','totalAssets','totalSupply','decimals']
    res=multicall(e,[(a,calldata(k+'()')) for a in candidates for k in fields],block)
    rows=[];rejected=[]
    for i,a in enumerate(candidates):
        raw=dict(zip(fields,res[4*i:4*i+4]));d={k:scalar(v) for k,v in raw.items()}
        if not d['asset'] or d['asset']>=2**160 or d['totalAssets'] is None or d['totalSupply'] is None or d['decimals'] is None or d['decimals']>36:
            rejected.append({'address':a,'reason':'incomplete ERC4626 read interface','raw':raw});continue
        d.update({'address':a,'asset':addr(d['asset']),'discovery':discovery['vault_candidates'][a]});rows.append(d)
    tokens=metadata(e,sorted({r['asset'] for r in rows}|{r['address'] for r in rows}),block)
    calls=[]
    for r in rows:
        a=r['address'];sample=10**r['decimals'];under_dec=tokens[r['asset']]['decimals']
        calls.extend([(a,calldata('previewRedeem(uint256)',sample)),(a,calldata('convertToAssets(uint256)',sample)),
            (a,calldata('maxDeposit(address)',MULTICALL)),(a,calldata('maxWithdraw(address)',MULTICALL)),
            (r['asset'],calldata('balanceOf(address)',a)),(a,calldata('balanceOf(address)',a)),
            (a,calldata('profitMaxUnlockTime()')),(a,calldata('fullProfitUnlockDate()')),
            (a,calldata('profitUnlockingRate()')),(a,calldata('lastReport()')),
            (a,calldata('maxRedeem(address)',a)),(a,calldata('convertToAssets(uint256)',r['totalSupply']))])
    res=multicall(e,calls,block)
    keys=['previewRedeem_share_unit','convertToAssets_share_unit','maxDeposit_probe','maxWithdraw_probe',
          'idle_assets','self_held_shares','profitMaxUnlockTime','fullProfitUnlockDate','profitUnlockingRate',
          'lastReport','maxRedeem_self','convertToAssets_totalSupply']
    for i,r in enumerate(rows):
        r.update({k:scalar(v) for k,v in zip(keys,res[i*len(keys):(i+1)*len(keys)])})
        r['metadata']=tokens[r['address']];r['asset_metadata']=tokens[r['asset']]
        dec=r['asset_metadata']['decimals']
        if dec is not None and dec<=36:
            r['assets_units']=r['totalAssets']/10**dec
            r['idle_units']=r['idle_assets']/10**dec if r['idle_assets'] is not None else None
            r['nav_per_share']=r['previewRedeem_share_unit']/10**dec if r['previewRedeem_share_unit'] is not None else None
    return {'vaults':rows,'rejected_event_emitters':rejected,'tokens':tokens}


def inspect_markets(e,discovery,block):
    ids=sorted(discovery['morpho_market_ids'])
    res=multicall(e,[(MORPHO,calldata(sig,id)) for id in ids for sig in ['idToMarketParams(bytes32)','market(bytes32)']],block)
    rows=[]
    for i,id in enumerate(ids):
        p=words(res[2*i]);s=words(res[2*i+1])
        if not p[0]:continue
        rows.append({'id':id,'loan':addr(p[0]),'collateral':addr(p[1]),'oracle':addr(p[2]),'irm':addr(p[3]),'lltv':p[4]/1e18,
            'supply_assets_raw':s[0],'borrow_assets_raw':s[2],'last_update':s[4],'fee':s[5]/1e18,
            'activity_events':discovery['morpho_market_ids'][id]})
    tokens=metadata(e,sorted({r['loan'] for r in rows}|{r['collateral'] for r in rows if int(r['collateral'],16)}),block)
    oracles=sorted({r['oracle'] for r in rows if int(r['oracle'],16)})
    keys=['price','BASE_VAULT','QUOTE_VAULT','BASE_VAULT_CONVERSION_SAMPLE','QUOTE_VAULT_CONVERSION_SAMPLE',
          'BASE_FEED_1','BASE_FEED_2','QUOTE_FEED_1','QUOTE_FEED_2','SCALE_FACTOR']
    data=multicall(e,[(o,calldata(k+'()')) for o in oracles for k in keys],block)
    od={o:{k:scalar(v) for k,v in zip(keys,data[i*len(keys):(i+1)*len(keys)])} for i,o in enumerate(oracles)}
    for r in rows:
        r['loan_metadata']=tokens[r['loan']];r['collateral_metadata']=tokens.get(r['collateral'])
        loan_dec=r['loan_metadata']['decimals'];col_dec=(r['collateral_metadata'] or {}).get('decimals')
        if loan_dec is not None:
            r['supply_units']=r['supply_assets_raw']/10**loan_dec;r['borrow_units']=r['borrow_assets_raw']/10**loan_dec
        op=od.get(r['oracle'],{}).get('price')
        if op is not None and col_dec is not None and loan_dec is not None:
            r['oracle_loan_units_per_collateral']=op/10**(36+loan_dec-col_dec)
    return {'markets':rows,'oracles':od,'tokens':tokens}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=OUT)
    p.add_argument('--offline',action='store_true');p.add_argument('--discover-only',action='store_true')
    a=p.parse_args();e=Evidence(a.out,a.offline)
    assert e.get('eth_chainId',[])=='0x1'
    h=e.get('eth_getBlockByNumber',['finalized',False]);block=int(h['number'],16)
    save(a.out,'snapshot.json',{'number':block,'hash':h['hash'],'timestamp':int(h['timestamp'],16)})
    d=discover(a.out,block)
    print(json.dumps({'block':block,'scope':d['scope'],'vault_candidates':len(d['vault_candidates']),
        'morpho_markets':len(d['morpho_market_ids'])}),flush=True)
    if a.discover_only:return
    v=inspect_vaults(e,d,block);save(a.out,'vaults.json',v)
    print('vault interfaces',len(v['vaults']),'nonzero assets',sum(r['totalAssets']>0 for r in v['vaults']),flush=True)
    m=inspect_markets(e,d,block);save(a.out,'markets.json',m)
    print('Morpho markets',len(m['markets']),'oracles',len(m['oracles']),flush=True)
    save(a.out,'sha256.json',{str(p.relative_to(a.out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((a.out/'raw').glob('*.json'))})


if __name__=='__main__':main()
