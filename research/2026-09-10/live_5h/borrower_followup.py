"""Pinned token-level exposure for two recurring Aave accounts and the largest low-HF Spark account."""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'scripts'))
from live_rpc import RPC,word
from live_scan import AAVE_POOL, SPARK_POOL, SEL, sel, enc_addr, TOKENS

hs=json.loads((OUT/'head_state.json').read_text())
blk=hex(hs['block'])
rpc=RPC(log_path=OUT/'rpc_errors.jsonl',max_credits=25000)
accounts=[('Aave v3',AAVE_POOL,'0xcf0a12cbd8088fc5f84ad431e71787157041cd69'),
          ('Aave v3',AAVE_POOL,'0xca686974913389d42f3c5f61010503daccdb487a'),
          ('SparkLend',SPARK_POOL,'0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7')]
result={'block':hs['block'],'block_hash':hs['block_hash'],'accounts':[]}
for venue,pool,account in accounts:
    reserves=hs['lending'][venue]
    provider=rpc.eth_calls([(pool,sel('ADDRESSES_PROVIDER()'))],blk)[0]
    provider='0x'+provider[-40:]
    oracle=rpc.eth_calls([(provider,sel('getPriceOracle()'))],blk)[0]
    oracle='0x'+oracle[-40:]
    unit=word(rpc.eth_calls([(oracle,sel('BASE_CURRENCY_UNIT()'))],blk)[0],0)
    assert unit>0
    health,config=rpc.eth_calls([(pool,SEL['getUserAccountData']+enc_addr(account)),
                               (pool,sel('getUserConfiguration(address)')+enc_addr(account))],blk)
    assert health and config
    calls=[]
    for token,row in reserves.items():
        calls += [(row['aToken'],SEL['balanceOf']+enc_addr(account)),
                  (row['variableDebt'],SEL['balanceOf']+enc_addr(account))]
    balances=rpc.eth_calls(calls,blk)
    positions=[]
    for i,(token,row) in enumerate(reserves.items()):
        supply,debt=balances[2*i:2*i+2]
        if not supply or not debt:
            raise RuntimeError('missing balance read')
        supply,debt=word(supply,0),word(debt,0)
        if supply or debt:
            data,price=rpc.eth_calls([(pool,SEL['getReserveData']+enc_addr(token)),
                                      (oracle,sel('getAssetPrice(address)')+enc_addr(token))],blk)
            assert data and price
            rid=word(data,7)
            enabled=bool(word(config,0)&(1<<(2*rid+1)))
            dec=TOKENS[token][1]
            px=word(price,0)/unit
            positions.append({'token':token,'symbol':TOKENS[token][0],'supply_raw':str(supply),'debt_raw':str(debt),
                              'supplied':supply/10**dec,'variable_debt':debt/10**dec,'oracle_usd':px,
                              'supply_usd':supply/10**dec*px,'debt_usd':debt/10**dec*px,
                              'reserve_id':rid,'collateral_enabled':enabled})
    hc,hd=word(health,0)/unit,word(health,1)/unit
    sc=sum(x['supply_usd'] for x in positions if x['collateral_enabled'])
    sd=sum(x['debt_usd'] for x in positions)
    result['accounts'].append({'venue':venue,'account':account,'oracle':oracle,'base_currency_unit':unit,
                              'health_raw':health,'config_raw':config,
                              'health_factor':word(health,5)/1e18,'collateral_usd':hc,'debt_usd':hd,
                              'positions':positions,'collateral_reconciliation_usd':sc-hc,'debt_reconciliation_usd':sd-hd,
                              'reconciles':abs(sc-hc)<=max(hc*.001,1) and abs(sd-hd)<=max(hd*.001,1)})
result['note']='Only registered reserves and variable debt are inventoried; reconcile against aggregate account data before asserting coverage. Oracle values and flags are pinned to the same block.'
result['rpc']=rpc.stats()
(OUT/'borrower_followup.json').write_text(json.dumps(result,indent=1))
print(json.dumps(result,indent=1))
assert all(x['reconciles'] for x in result['accounts'])
