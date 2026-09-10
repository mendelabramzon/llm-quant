"""Historical cash/rate checks for the rejected PYUSD episode and rETH exit."""
import json,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT.parents[2]/'scripts'))
from live_rpc import RPC,word
from live_scan import AAVE_POOL,SEL,sel,enc_addr
from window_raw import Window,RESERVE_DATA_UPDATED,hx
hs=json.loads((OUT/'head_state.json').read_text())
rpc=RPC(log_path=OUT/'rpc_errors.jsonl',max_credits=6000)
pyusd='0x6c3ea9036406852006290770bedfcaba0e23a0e8'
at=hs['lending']['Aave v3'][pyusd]['aToken']
reth=hs['rates']['RETH']['contract']
result={'block':hs['block'],'block_hash':hs['block_hash'],'pyusd':[]}
for n in (25945520,25946281,hs['block']):
 data,cash=rpc.eth_calls([(AAVE_POOL,SEL['getReserveData']+enc_addr(pyusd)),
                         (pyusd,SEL['balanceOf']+enc_addr(at))],hex(n))
 assert data and cash
 logs=Window(OUT)._read('logs',n)
 events=[{'log_index':hx(l['logIndex']),'tx':l['transactionHash'],'borrow_apr':word(l['data'],2)/1e27}
         for l in logs if len(l.get('topics',[]))==2 and l['topics'][0]==RESERVE_DATA_UPDATED
         and l['topics'][1].endswith(pyusd[2:])]
 result['pyusd'].append({'block':n,'end_borrow_apr':word(data,4)/1e27,'cash_pyusd':word(cash,0)/1e6,
                         'updates':events,'raw_reserve_data':data,'raw_cash':cash})
cash,rate=rpc.eth_calls([(reth,sel('getTotalCollateral()')),(reth,sel('getExchangeRate()'))],hex(hs['block']))
assert cash and rate
result['reth']={'contract':reth,'collateral_eth':word(cash,0)/1e18,'exchange_rate':word(rate,0)/1e18,
 'raw_collateral':cash,'raw_rate':rate,'method':'getTotalCollateral(): rETH ETH plus deposit-pool excess ETH',
 'source':'https://github.com/rocket-pool/rocketpool/blob/master/contracts/contract/token/RocketTokenRETH.sol',
 'note':'Snapshot collateral is a protocol ceiling; no executable buy-and-burn quote was simulated.'}
result['rpc']=rpc.stats()
(OUT/'liquidity_followup.json').write_text(json.dumps(result,indent=1)+'\n')
print(json.dumps(result,indent=1))
