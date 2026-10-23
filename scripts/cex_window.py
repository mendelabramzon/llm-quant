"""Trailing-window CEX snapshot: what moved on Binance/Bybit USDT perps over the last N hours.

Writes <out>/cex.json: per-symbol N-hour return, volume in the window vs the trailing 24h rate, open-interest change
(Bybit 1h series), current and predicted funding on both venues, and the perp-vs-spot basis on Binance. Public
endpoints only, no keys. The point is to say which markets carried the window and whether any of them left a
dislocation that survives a late entry (funding or basis that persists after the move), not to trade the move.
"""
import argparse, json, time, statistics
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1 + i)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--hours', type=float, default=2)
    ap.add_argument('--top', type=int, default=200, help='symbols by 24h quote volume on Binance')
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - int(a.hours * 3600e3)

    t24 = {t['symbol']: t for t in get('https://fapi.binance.com/fapi/v1/ticker/24hr') if t['symbol'].endswith('USDT') and t['symbol'].isascii()}
    prem = {p['symbol']: p for p in get('https://fapi.binance.com/fapi/v1/premiumIndex')}
    spot = {t['symbol']: float(t['price']) for t in get('https://api.binance.com/api/v3/ticker/price')}
    by = {t['symbol']: t for t in get('https://api.bybit.com/v5/market/tickers?category=linear')['result']['list']}
    syms = sorted(t24, key=lambda s: -float(t24[s]['quoteVolume']))[:a.top]

    def one(s):
        k = get(f'https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=5m&startTime={start_ms - 300000}&limit=1000')
        k = [x for x in k if x[0] >= start_ms - 300000]
        if len(k) < 3:
            return None
        o, c = float(k[0][1]), float(k[-1][4])
        hi, lo = max(float(x[2]) for x in k), min(float(x[3]) for x in k)
        qv = sum(float(x[7]) for x in k)
        rets = [float(x[4]) / float(x[1]) - 1 for x in k]
        p = prem.get(s, {}); b = by.get(s, {})
        mark = float(p.get('markPrice') or c)
        sp = spot.get(s)
        oi = None
        try:
            oih = get(f'https://api.bybit.com/v5/market/open-interest?category=linear&symbol={s}&intervalTime=1h&limit=4')['result']['list']
            if len(oih) >= 3:
                oi = float(oih[0]['openInterest']) / float(oih[2]['openInterest']) - 1
        except Exception:
            pass
        return {
            'symbol': s, 'ret': c / o - 1, 'range': hi / lo - 1, 'max_5m_abs': max(abs(r) for r in rets),
            'quote_vol_window': qv, 'vol_ratio': qv / (float(t24[s]['quoteVolume']) * a.hours / 24 or 1),
            'ret_24h': float(t24[s]['priceChangePercent']) / 100,
            'funding_bn': float(p['lastFundingRate']) if p.get('lastFundingRate') else None,
            'funding_by': float(b['fundingRate']) if b.get('fundingRate') else None,
            'basis_bn': (mark / sp - 1) if sp else None,
            'oi_by_usd': float(b['openInterestValue']) if b.get('openInterestValue') else None,
            'oi_chg_2h_by': oi, 'last': c,
        }

    with ThreadPoolExecutor(8) as ex:
        rows = [r for r in ex.map(one, syms) if r]
    btc = next((r['ret'] for r in rows if r['symbol'] == 'BTCUSDT'), 0)
    for r in rows:
        r['excess_vs_btc'] = r['ret'] - btc
    res = {'generated_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'hours': a.hours,
           'window_start_ms': start_ms, 'end_ms': now_ms, 'n': len(rows),
           'median_ret': statistics.median(r['ret'] for r in rows), 'btc_ret': btc, 'rows': rows}
    (out / 'cex.json').write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != 'rows'}))

if __name__ == '__main__':
    main()
