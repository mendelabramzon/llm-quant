#!/usr/bin/env python3
"""Read-only, block-pinned screen for returns that do not require transaction ordering.

Public RPC for state; existing local Infura configuration is a log-query fallback.
Preserves raw responses and replays offline. No transaction signing.
Usage: uv run --with pycryptodome python scripts/non_mev_screen.py [--offline]
Use a new --out directory for another snapshot. Successful responses are reused;
failed log requests can be retried, preserving their errors in the same record.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

from Crypto.Hash import keccak
from drpc import rpc, ENDPOINTS

ROOT = Path(__file__).resolve().parents[1]
YEAR = 365 * 86400
RAY = 10**27
WAD = 10**18
ZERO = '0x' + '0' * 40
AAVE = '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
SPARK = '0xc13e21b648a5ee794902342038ff3adab66be987'
TOKENS = {
    'USDC': ('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 6),
    'USDT': ('0xdac17f958d2ee523a2206206994597c13d831ec7', 6),
    'DAI': ('0x6b175474e89094c44da98b954eedeac495271d0f', 18),
    'PYUSD': ('0x6c3ea9036406852006290770bedfcaba0e23a0e8', 6),
    'RLUSD': ('0x8292bb45bf1ee4d140127049757c2e0ff06317ed', 18),
    'USDS': ('0xdc035d45d973e3ec169d2276ddab16f1e407384f', 18),
    'USDe': ('0x4c9edd5852cd905f086c759e8383e09bff1e68b3', 18),
}
COMETS = {'USDC': '0xc3d688b66703497daa19211eedff47f25384cdc3',
          'USDT': '0x3afdc9bca9213a35503b077a6072f3d0d5ab0840'}
SDAI = '0x83f20f44975d03b1b09e64809b757c47f942beea'
SUSDE = '0x9d39a5de30e57443bff2a8307a4256c8797a3497'
BUY_POOL = '0x167478921b907422f8e88b43c4af2b8bea278d3a'
EXIT_POOL = '0x5b03cccab7ba3010fa5cad23746cbf0794938e96'
FEED = '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'


def digest(s):
    return keccak.new(digest_bits=256, data=s.encode()).hexdigest()


def calldata(signature, *args):
    return '0x' + digest(signature)[:8] + ''.join(
        (x[2:] if isinstance(x, str) else f'{x:064x}').rjust(64, '0') for x in args)


def words(s):
    if not isinstance(s, str) or not s.startswith('0x') or (len(s) - 2) % 64:
        raise ValueError('Malformed ABI response')
    return [int(s[i:i + 64], 16) for i in range(2, len(s), 64)]


def addr(n):
    return f'0x{n:040x}'


def string(s):
    b = bytes.fromhex(s[2:])
    if len(b) == 32:
        return b.rstrip(b'\0').decode()
    offset = int.from_bytes(b[:32], 'big')
    length = int.from_bytes(b[offset:offset+32], 'big')
    return b[offset+32:offset+32+length].decode()


class Evidence:
    def __init__(self, out, offline=False):
        self.out, self.offline = out, offline
        (out / 'raw').mkdir(parents=True, exist_ok=True)
        self.hits = self.requests = 0
        self.log_rpc = None

    def get(self, method, params):
        assert method in {'eth_call', 'eth_chainId', 'eth_getBlockByNumber',
                          'eth_getCode', 'eth_getStorageAt', 'eth_getLogs'}
        key = json.dumps([method, params], sort_keys=True)
        path = self.out / 'raw' / (hashlib.sha256(key.encode()).hexdigest() + '.json')
        if path.exists():
            record = json.loads(path.read_text())
            self.hits += 1
        else:
            if self.offline:
                raise RuntimeError('Offline cache miss: ' + key)
            try:
                result = rpc(method, params, timeout=20, retries=1)
                record = {'method': method, 'params': params, 'result': result}
            except Exception as exc:
                record = {'method': method, 'params': params, 'error': str(exc)}
            path.write_text(json.dumps(record, indent=2) + '\n')
            self.requests += 1
        if method == 'eth_getLogs' and 'error' in record and not self.offline:
            attempts = record.get('previous_errors', []) + [record['error']]
            for endpoint in ENDPOINTS + ['Infura (existing local configuration)']:
                try:
                    if endpoint.startswith('Infura'):
                        from live_rpc import RPC
                        if self.log_rpc is None:
                            self.log_rpc = RPC(max_credits=10000, interval=.2, timeout=20)
                        result = self.log_rpc.call(method, params)
                    else:
                        result = rpc(method, params, endpoints=[endpoint], timeout=20, retries=1)
                    record = {'method':method,'params':params,'result':result,
                              'endpoint':endpoint,'previous_errors':attempts}
                    path.write_text(json.dumps(record,indent=2)+'\n')
                    self.requests += 1
                    break
                except Exception as exc:
                    attempts.append({'endpoint':endpoint,'error':str(exc)})
            else:
                record['previous_errors'] = attempts
                path.write_text(json.dumps(record,indent=2)+'\n')
        if 'error' in record:
            raise RuntimeError(record['error'])
        return record['result']

    def call(self, to, sig, *args, block, optional=False):
        try:
            return words(self.get('eth_call', [{'to': to, 'data': calldata(sig, *args)}, hex(block)]))
        except RuntimeError:
            if optional:
                return None
            raise

    def header(self, n):
        h = self.get('eth_getBlockByNumber', [hex(n), False])
        return {'number': int(h['number'], 16), 'hash': h['hash'],
                'timestamp': int(h['timestamp'], 16), 'base_fee': int(h['baseFeePerGas'], 16)}


def first_at(e, timestamp, head):
    # Binary search, using observed headers, not assumed twelve-second block times.
    lo = max(0, head['number'] - math.ceil((head['timestamp'] - timestamp) / 12) - 1024)
    hi = head['number']
    assert e.header(lo)['timestamp'] <= timestamp <= head['timestamp']
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if e.header(mid)['timestamp'] < timestamp:
            lo = mid
        else:
            hi = mid
    return e.header(hi)


def aave_rate(row, added=0):
    c = row['curve']
    debt, cash = row['borrowed'], row['rate_cash'] + added
    u = debt / (debt + cash) if debt else 0
    supply_u = debt / (debt + cash + row['unbacked']) if debt else 0
    borrow = c['base'] + (c['slope1'] * u / c['optimal'] if u <= c['optimal'] else
                         c['slope1'] + c['slope2'] * (u - c['optimal']) / (1 - c['optimal']))
    return borrow * supply_u * (1 - row['reserve_factor']), borrow


def reserve(e, venue, pool, sym, block, history):
    token, dec = TOKENS[sym]
    data = e.call(pool, 'getReserveData(address)', token, block=block)
    if len(data) < 15 or not data[8]:
        return None
    at, debt, strategy = addr(data[8]), addr(data[10]), addr(data[11])
    conf = data[0]
    assert (conf >> 48) & 255 == dec
    supplied = e.call(at, 'totalSupply()', block=block)[0] / 10**dec
    borrowed = e.call(debt, 'totalSupply()', block=block)[0] / 10**dec
    cash = e.call(token, 'balanceOf(address)', at, block=block)[0] / 10**dec
    virtual = e.call(pool, 'getVirtualUnderlyingBalance(address)', token, block=block, optional=True)
    curve = e.call(strategy, 'getInterestRateData(address)', token, block=block, optional=True)
    if curve and len(curve) == 4:
        curve = dict(zip(['optimal', 'base', 'slope1', 'slope2'], [x / RAY for x in curve]))
    else:
        values = [e.call(strategy, sig, block=block, optional=True) for sig in
                  ['OPTIMAL_USAGE_RATIO()', 'getBaseVariableBorrowRate()',
                   'getVariableRateSlope1()', 'getVariableRateSlope2()']]
        curve = dict(zip(['optimal', 'base', 'slope1', 'slope2'], [x[0]/RAY for x in values])) if all(values) else None
    row = {'venue': venue, 'symbol': sym, 'pool': pool, 'token': token, 'a_token': at,
           'debt_token': debt, 'strategy': strategy, 'supply_apr': data[2]/RAY,
           'borrow_apr': data[4]/RAY, 'supplied': supplied, 'borrowed': borrowed,
           'cash': cash, 'rate_cash': virtual[0]/10**dec if virtual else cash,
           'unbacked': data[13]/10**dec, 'reserve_factor': ((conf >> 64) & 65535)/10000,
           'supply_cap': (conf >> 116) & ((1 << 36)-1),
           'active': bool((conf >> 56) & 1), 'frozen': bool((conf >> 57) & 1),
           'paused': bool((conf >> 60) & 1), 'curve': curve}
    # Income indexes measure actual historical interest for a continuously held aToken.
    ix_now = e.call(pool, 'getReserveNormalizedIncome(address)', token, block=block)[0]
    row['realized_supply_history'] = []
    for h in history:
        ix = e.call(pool, 'getReserveNormalizedIncome(address)', token, block=h['number'])[0]
        elapsed = e.header(block)['timestamp'] - h['timestamp']
        row['realized_supply_history'].append({'block': h['number'], 'elapsed_seconds': elapsed,
            'start_index': str(ix), 'end_index': str(ix_now),
            'return': (ix_now-ix)/ix, 'simple_annualized': (ix_now-ix)/ix*YEAR/elapsed})
    if curve and curve['optimal']:
        modeled, _ = aave_rate(row)
        row['model_minus_stored_rate_bps'] = (modeled - row['supply_apr'])*10000
        row['supply_to_kink'] = max(0, borrowed/curve['optimal'] - borrowed - row['rate_cash'])
        row['supply_size_scenarios'] = [{'added': x, 'supply_apr': aave_rate(row, x)[0]}
                                       for x in [10000, 100000, 1000000, 10000000]]
    return row


def comet_rate(row, added=0):
    u = row['borrowed']/(row['supplied']+added)
    c = row['curve']
    return (c['base'] + c['low']*min(u,c['kink']) + c['high']*max(0,u-c['kink']))*YEAR/WAD


def comet(e, sym, address, block, history):
    token, dec = TOKENS[sym]
    assert addr(e.call(address, 'baseToken()', block=block)[0]) == token
    d = {k: e.call(address, sig, block=block)[0] for k, sig in {
        'supplied_raw': 'totalSupply()', 'borrowed_raw': 'totalBorrow()', 'util_raw': 'getUtilization()',
        'base': 'supplyPerSecondInterestRateBase()', 'low': 'supplyPerSecondInterestRateSlopeLow()',
        'high': 'supplyPerSecondInterestRateSlopeHigh()', 'kink_raw': 'supplyKink()',
        'supply_paused': 'isSupplyPaused()', 'withdraw_paused': 'isWithdrawPaused()'}.items()}
    row = {'venue': 'Compound v3', 'symbol': sym, 'contract': address, 'token': token,
           'supplied': d['supplied_raw']/10**dec, 'borrowed': d['borrowed_raw']/10**dec,
           'utilization': d['util_raw']/WAD, 'curve': {'base':d['base'],'low':d['low'],
           'high':d['high'],'kink':d['kink_raw']/WAD},
           'supply_paused':bool(d['supply_paused']), 'withdraw_paused':bool(d['withdraw_paused']),
           'cash':e.call(token,'balanceOf(address)',address,block=block)[0]/10**dec,
           'supply_apr':e.call(address,'getSupplyRate(uint256)',d['util_raw'],block=block)[0]*YEAR/WAD,
           'borrow_apr':e.call(address,'getBorrowRate(uint256)',d['util_raw'],block=block)[0]*YEAR/WAD}
    row['spot_history'] = []
    for h in history:
        u=e.call(address,'getUtilization()',block=h['number'])[0]
        r=e.call(address,'getSupplyRate(uint256)',u,block=h['number'])[0]*YEAR/WAD
        row['spot_history'].append({'block':h['number'],'timestamp':h['timestamp'],'supply_apr':r})
    row['size_scenarios'] = []
    for amount in [0,10000,100000,1000000,10000000,25000000,50000000]:
        u = d['borrowed_raw']*WAD//(d['supplied_raw']+amount*10**dec)
        direct=e.call(address,'getSupplyRate(uint256)',u,block=block)[0]*YEAR/WAD
        modeled=comet_rate(row,amount)
        assert abs(direct-modeled)<1e-9
        row['size_scenarios'].append({'added':amount,'supply_apr':direct})
    return row


def midnight(e, out):
    source=ROOT/'research/2026-09-06/live/midnight_2026-09-06.json'
    original=source.read_bytes()
    d=json.loads(original)
    raw=[]
    for first in range(d['blocks'][0],d['blocks'][1]+1,50):
        raw.extend(e.get('eth_getLogs',[{'address':AAVE,'fromBlock':hex(first),
            'toBlock':hex(min(first+49,d['blocks'][1])),
            'topics':['0x'+digest('ReserveDataUpdated(address,uint256,uint256,uint256,uint256,uint256)'),
            '0x'+TOKENS['USDC'][0][2:].rjust(64,'0')]}]))
    raw.sort(key=lambda r:(int(r['blockNumber'],16),int(r['logIndex'],16)))
    assert len(raw)==len(d['aave_usdc_rates'])
    for log, saved in zip(raw,d['aave_usdc_rates']):
        w=words(log['data'])
        assert int(log['blockNumber'],16)==saved['block']
        assert w[0]/RAY==saved['supply_apr'] and w[2]/RAY==saved['borrow_apr']
    # Preserve order in each block. Only the final emitted rate applies after its timestamp.
    by_time={}
    for r in d['aave_usdc_rates']:
        by_time[int(dt.datetime.fromisoformat(r['utc']).timestamp())]=r
    times=sorted(by_time)
    baseline=by_time[times[0]]
    area={k:0.0 for k in ['supply_apr','borrow_apr']}
    for left,right in zip(times,times[1:]):
        for k in area:
            area[k] += (by_time[left][k]-baseline[k])*(right-left)/YEAR
    ops=d['aave_usdc_ops_10m_plus']
    start=next(x['block'] for x in ops if x['kind']=='withdraw')-1
    end=next(x['block'] for x in ops if x['kind']=='supply')
    token=TOKENS['USDC'][0]
    hs,he=e.header(start),e.header(end)
    elapsed=he['timestamp']-hs['timestamp']
    i0=e.call(AAVE,'getReserveNormalizedIncome(address)',token,block=start)[0]
    i1=e.call(AAVE,'getReserveNormalizedIncome(address)',token,block=end)[0]
    loan0=e.call(AAVE,'getReserveNormalizedVariableDebt(address)',token,block=start)[0]
    loan1=e.call(AAVE,'getReserveNormalizedVariableDebt(address)',token,block=end)[0]
    result={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(original).hexdigest(),
            'observed_event_count':len(d['aave_usdc_rates']), 'independently_matched_rpc_logs':len(raw),
            'end_of_timestamp_count':len(times),
            'baseline':baseline,'integral_interval_seconds':times[-1]-times[0],
            'incremental_supply_return':area['supply_apr'],'incremental_borrow_cost':area['borrow_apr'],
            'incremental_supply_per_million':area['supply_apr']*1e6,
            'incremental_borrow_per_million':area['borrow_apr']*1e6,
            'source_operations':ops,'index_check':{'start':hs,'end':he,'elapsed_seconds':elapsed,
            'supply_return':(i1-i0)/i0,'borrow_return':(loan1-loan0)/loan0,
            'excess_supply_return':(i1-i0)/i0-baseline['supply_apr']*elapsed/YEAR,
            'excess_borrow_cost':(loan1-loan0)/loan0-baseline['borrow_apr']*elapsed/YEAR}}
    (out/'midnight.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def redemption(e, block, gas_usd):
    # Quotes at the same state are a screen; tomorrow's exit price is not fixed by them.
    assert addr(e.call(SUSDE,'asset()',block=block)[0]) == TOKENS['USDe'][0]
    assert addr(e.call(SDAI,'asset()',block=block)[0]) == TOKENS['DAI'][0]
    for pool, expected in [(BUY_POOL,[SDAI,SUSDE]),(EXIT_POOL,[TOKENS['USDT'][0],TOKENS['USDe'][0]])]:
        assert [addr(e.call(pool,'coins(uint256)',i,block=block)[0]) for i in [0,1]] == expected
    cd=e.call(SUSDE,'cooldownDuration()',block=block)[0]
    result={'cooldown_seconds':cd,'buy_pool':BUY_POOL,'exit_pool':EXIT_POOL,
            'start_asset':'sDAI, valued by redeemable DAI','end_asset':'USDT',
            'stablecoin_parity_assumed':True,'future_exit_price_guaranteed':False,
            'includes_DAI_USDT_basis_hedge':False,'capital_hurdle_apr':0.05,'gas_budget_usd':gas_usd,
            'scenarios':[]}
    nav=e.call(SDAI,'previewRedeem(uint256)',WAD,block=block)[0]
    for target in [10000,100000,250000,500000]:
        shares=target*WAD*WAD//nav
        cost=e.call(SDAI,'previewRedeem(uint256)',shares,block=block)[0]/WAD
        bought=e.call(BUY_POOL,'get_dy(int128,int128,uint256)',0,1,shares,block=block)[0]
        locked=e.call(SUSDE,'previewRedeem(uint256)',bought,block=block)[0]
        proceeds=e.call(EXIT_POOL,'get_dy(int128,int128,uint256)',1,0,locked,block=block)[0]/1e6
        carry=cost*.05*cd/YEAR
        result['scenarios'].append({'cost_dai':cost,'input_sdai_raw':str(shares),'bought_susde_raw':str(bought),
            'locked_usde':locked/WAD,'quoted_usdt_exit':proceeds,
            'entry_discount_bps':(locked/WAD/cost-1)*10000,
            'quoted_pnl_before_gas_and_carry':proceeds-cost,
            'capital_cost':carry,'screened_net':proceeds-cost-carry-gas_usd,
            'exit_price_haircut_10bps_net':proceeds*.999-cost-carry-gas_usd})
    return result


def same_asset_routes(lending, comets, gas):
    routes=[]
    for source in lending+comets:
        for dest in lending+comets:
            if source['symbol']!=dest['symbol'] or source['venue']==dest['venue']:
                continue
            if dest['supply_apr']<=source['supply_apr']:
                continue
            if dest['venue']=='Compound v3':
                enabled=not dest['supply_paused'] and not dest['withdraw_paused']
                rate=lambda x:comet_rate(dest,x)
                capacity=100_000_000
            else:
                enabled=dest['active'] and not dest['frozen'] and not dest['paused'] and bool(dest['curve'])
                rate=lambda x:aave_rate(dest,x)[0]
                capacity=max(0,dest['supply_cap']-dest['supplied']) if dest['supply_cap'] else 100_000_000
            if not enabled:
                continue
            scenarios=[]
            for size in [10000,100000,1000000,10000000]:
                if size>min(source['cash'],capacity):
                    continue
                apr=rate(size);daily=size*(apr-source['supply_apr'])/365
                scenarios.append({'amount':size,'post_deposit_apr':apr,'incremental_daily':daily,
                    'seven_day_net_static':daily*7-gas,'break_even_days':gas/daily if daily>0 else None})
            routes.append({'symbol':source['symbol'],'from':source['venue'],'to':dest['venue'],
                'source_apr':source['supply_apr'],'destination_spot_apr':dest['supply_apr'],
                'source_cash':source['cash'],'destination_deposit_headroom':capacity,'scenarios':scenarios})
    return routes


def savings(e, block, history):
    vault='0xa3931d71877c0e7a3148cb7eb4463524fec27fbd'
    assert addr(e.call(vault,'asset()',block=block)[0])==TOKENS['USDS'][0]
    ssr=e.call(vault,'ssr()',block=block)[0]
    current=e.call(vault,'previewRedeem(uint256)',WAD,block=block)[0]
    return {'vault':vault,'asset':'USDS','ssr_ray':str(ssr),'apy':math.expm1(math.log(ssr/RAY)*YEAR),
            'max_deposit_raw':str(e.call(vault,'maxDeposit(address)','0x'+'0'*36+'1234',block=block)[0]),
            'total_assets':e.call(vault,'totalAssets()',block=block)[0]/WAD,
            'history':[{'block':h['number'],'share_return':current/e.call(vault,'previewRedeem(uint256)',WAD,block=h['number'])[0]-1}
                       for h in history]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'research/2026-09-06/non_mev')
    p.add_argument('--offline',action='store_true')
    args=p.parse_args();e=Evidence(args.out,args.offline)
    assert e.get('eth_chainId',[])=='0x1'
    h=e.get('eth_getBlockByNumber',['finalized',False]);block=int(h['number'],16)
    head=e.header(block)
    assert head['hash']==h['hash']
    history=[first_at(e,head['timestamp']-hours*3600,head) for hours in [6,24]]
    print('Snapshot',block,dt.datetime.fromtimestamp(head['timestamp'],dt.timezone.utc).isoformat(),flush=True)
    # Verify metadata before interpreting amounts.
    for symbol,(token,dec) in TOKENS.items():
        assert e.call(token,'decimals()',block=block)[0]==dec
        actual=string(e.get('eth_call',[{'to':token,'data':calldata('symbol()')},hex(block)]))
        assert actual==symbol,(symbol,actual)
    lending=[]
    for venue,pool,symbols in [('Aave v3',AAVE,list(TOKENS)),('SparkLend',SPARK,['USDC','USDT','DAI','USDS','PYUSD'])]:
        for sym in symbols:
            r=reserve(e,venue,pool,sym,block,history)
            if r:
                lending.append(r)
                print(venue,sym,round(r['supply_apr']*100,4),flush=True)
    comets=[comet(e,sym,address,block,history) for sym,address in COMETS.items()]
    desc=string(e.get('eth_call',[{'to':FEED,'data':calldata('description()')},hex(block)]))
    assert desc=='ETH / USD'
    feed=e.call(FEED,'latestRoundData()',block=block)
    assert feed[1]>0 and feed[3]<=head['timestamp'] and head['timestamp']-feed[3]<86400
    eth=feed[1]/10**e.call(FEED,'decimals()',block=block)[0]
    # Budget, not an eth_estimateGas assertion: approvals + entry + later exit.
    gas=600000*(head['base_fee']+.1e9)/1e18*eth
    allocation=[]
    for c in comets:
        base=next(r for r in lending if r['venue']=='Aave v3' and r['symbol']==c['symbol'])
        candidates=[]
        for s in c['size_scenarios']:
            x=s['added'];spread=s['supply_apr']-base['supply_apr'];annual=x*spread
            candidates.append(dict(s,incremental_apr=spread,incremental_daily=annual/365,
                gas_break_even_days=gas/(annual/365) if annual>0 else None,
                seven_day_net_at_static_rates=annual*7/365-(gas if x else 0)))
        max_x=min(base['cash']*.8,100_000_000)
        # Uniform grid: optimum conditional on this state, no assumed future flows.
        best=max(({'amount':max_x*i/10000,'annual_increment':max_x*i/10000*(comet_rate(c,max_x*i/10000)-base['supply_apr'])}
                  for i in range(10001)),key=lambda r:r['annual_increment'])
        allocation.append({'asset':c['symbol'],'source':'Aave v3','destination':'Compound v3',
            'baseline_apr':base['supply_apr'],'source_cash':base['cash'],'destination_cash':c['cash'],
            'scenarios':candidates,'static_state_grid_optimum':best})
    red=redemption(e,block,gas)
    sky=savings(e,block,history)
    night=midnight(e,args.out)
    result={'head':head,'history_headers':history,'lending':lending,'compound':comets,
        'gas_assumption':{'units':600000,'tip_gwei':.1,'eth_usd':eth,'feed_updated':feed[3],'usd':gas},
        'same_asset_allocation':allocation,'all_same_asset_routes':same_asset_routes(lending,comets,gas),
        'savings_usds':sky,'redemption':red,'midnight':night,
        'limitations':['Read-only screen; companion fork tests simulate funded deposits but no live execution',
            'Future rates, withdrawals and DEX exit prices are uncertain',
            'No reward tokens, leverage, assumed hedge, or wallet balance in PnL',
            'RPC-provider evidence; finalized hash pinned, not local consensus verification']}
    (args.out/'evidence.json').write_text(json.dumps(result,indent=2)+'\n')
    hashes={str(f.relative_to(args.out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((args.out/'raw').glob('*.json'))}
    (args.out/'sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps({'block':block,'lending':len(lending),'compound':len(comets),
                      'raw_records':len(hashes),'new_requests':e.requests,'cache_hits':e.hits,'gas_usd':gas}))


if __name__=='__main__':
    main()
