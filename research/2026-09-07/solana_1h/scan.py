"""Read-only, resumable Solana block sample and offline transaction triage."""
import concurrent.futures as cf
import collections as co
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import random
import statistics
import sys
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
RPC = 'https://api.mainnet-beta.solana.com'
VOTE = 'Vote111111111111111111111111111111111111111'
SOL = 'So11111111111111111111111111111111111111112'
USDC = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
USDT = 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'
lock = threading.Lock()
next_at = 0

def save(name, obj):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if name.endswith('.gz'):
        with gzip.open(path, 'wt') as f:
            json.dump(obj, f, separators=(',', ':'))
    else:
        path.write_text(json.dumps(obj, indent=2))

def read(name):
    path = ROOT / name
    with (gzip.open(path, 'rt') if name.endswith('.gz') else path.open()) as f:
        return json.load(f)

def rpc(method, params):
    global next_at
    for attempt in range(5):
        with lock:
            delay = max(0, next_at - time.monotonic())
            next_at = time.monotonic() + delay + .38
        time.sleep(delay)
        try:
            req = urllib.request.Request(RPC, data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(), headers={'Content-Type':'application/json','Accept-Encoding':'gzip'})
            with urllib.request.urlopen(req, timeout=45) as r:
                body = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    body = gzip.decompress(body)
            result = json.loads(body)
            if 'error' in result:
                raise RuntimeError(str(result['error']))
            return result['result']
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(2 ** (attempt + 1))

def collect():
    m = read('manifest.json')
    if 'start_slot' not in m:
        lo, hi = m['end_slot'] - 16000, m['end_slot']
        while lo < hi:
            mid = (lo + hi) // 2
            slots = rpc('getBlocksWithLimit', [mid, 1, {'commitment':'finalized'}])
            slot = slots[0]
            stamp = rpc('getBlockTime', [slot])
            if stamp < m['start_ts']:
                lo = slot + 1
            else:
                hi = mid
        m['start_slot'] = rpc('getBlocksWithLimit', [lo, 1, {'commitment':'finalized'}])[0]
        m['start_slot_time'] = rpc('getBlockTime', [m['start_slot']])
        m['previous_slot_time'] = rpc('getBlockTime', [rpc('getBlocks', [m['start_slot'] - 20, m['start_slot'] - 1, {'commitment':'finalized'}])[-1]])
        slots = rpc('getBlocks', [m['start_slot'], m['end_slot'], {'commitment':'finalized'}])
        save('slots.json', slots)
        rng = random.Random(202609071243)
        n = 180
        chosen = [slots[rng.randrange(i * len(slots) // n, (i + 1) * len(slots) // n)] for i in range(n)]
        m.update(produced_blocks=len(slots), sample_slots=chosen, sampling='180 equal produced-block-index strata; one pseudorandom block per stratum; seed 202609071243')
        save('manifest.json', m)
    def get(slot):
        path = 'blocks/%s.json.gz' % slot
        if not (ROOT / path).exists():
            b = rpc('getBlock', [slot, {'commitment':'finalized','encoding':'jsonParsed','transactionDetails':'full','rewards':False,'maxSupportedTransactionVersion':0}])
            if not b or not m['start_ts'] <= b['blockTime'] <= m['end_ts']:
                raise ValueError('block outside pinned window or null: %s' % slot)
            save(path, b)
        return slot
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for i, slot in enumerate(ex.map(get, m['sample_slots']), 1):
            if i % 15 == 0:
                print('collected', i, '/', len(m['sample_slots']), 'slot', slot, flush=True)
    m['completed_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    m['block_file_sha256'] = {str(s):hashlib.sha256((ROOT / ('blocks/%s.json.gz' % s)).read_bytes()).hexdigest() for s in m['sample_slots']}
    save('manifest.json', m)

def feature(tx, slot, stamp):
    meta, msg = tx['meta'], tx['transaction']['message']
    keys = [a['pubkey'] for a in msg['accountKeys']]
    ixs = msg['instructions']
    if any(i['programId'] == VOTE for i in ixs):
        return None
    allix = ixs + [i for group in meta.get('innerInstructions') or [] for i in group['instructions']]
    signers = [a['pubkey'] for a in msg['accountKeys'] if a.get('signer')]
    tokens = {}
    for side, factor in [('preTokenBalances', -1), ('postTokenBalances', 1)]:
        for a in meta.get(side) or []:
            owner = a.get('owner', keys[a['accountIndex']])
            k = (owner, a['mint'])
            v = tokens.setdefault(k, [0, a['uiTokenAmount']['decimals']])
            v[0] += factor * int(a['uiTokenAmount']['amount'])
    deltas = [{'owner':o,'mint':mint,'raw':v[0],'decimals':v[1],'delta':v[0] / 10 ** v[1]} for (o,mint),v in tokens.items() if v[0]]
    native = [{'account':a,'delta':(post-pre)/1e9} for a,pre,post in zip(keys,meta['preBalances'],meta['postBalances']) if pre != post]
    native.sort(key=lambda x:abs(x['delta']), reverse=True)
    transfers = []
    for ix in allix:
        p = ix.get('parsed')
        if isinstance(p, dict) and p.get('type') in ('transfer','transferChecked','mintTo','mintToChecked','burn','burnChecked'):
            transfers.append({'program':ix.get('program'), **p})
    logs = meta.get('logMessages') or []
    events = [l for l in logs if l.startswith('Program log: Instruction:') or any(w in l.lower() for w in ['liquidat','flash loan','flashloan','insufficient','slippage','arbitrage'])]
    f = {'signature':tx['transaction']['signatures'][0], 'slot':slot,'time':stamp,'payer':keys[0],'signers':signers,'err':meta['err'],'fee_sol':meta['fee']/1e9,'cu':meta.get('computeUnitsConsumed',0),'top_programs':sorted({i['programId'] for i in ixs}),'programs':sorted({i['programId'] for i in allix}),'native':native,'tokens':deltas,'events':events,'transfers':transfers}
    f['max_sol_change'] = max([abs(x['delta']) for x in native] + [abs(x['delta']) for x in deltas if x['mint']==SOL] + [0])
    f['max_stable_change'] = max([abs(x['delta']) for x in deltas if x['mint'] in (USDC,USDT)] + [0])
    return f

def analyze():
    m = read('manifest.json')
    counts = co.Counter()
    programs = co.defaultdict(co.Counter)
    payers = co.defaultdict(co.Counter)
    bins = co.defaultdict(co.Counter)
    fees, features = [], []
    for slot in m['sample_slots']:
        path = 'blocks/%s.json.gz' % slot
        if not (ROOT / path).exists():
            continue
        b = read(path)
        counts['blocks'] += 1
        counts['transactions'] += len(b['transactions'])
        for tx in b['transactions']:
            f = feature(tx, slot, b['blockTime'])
            if f is None:
                counts['votes'] += 1
                continue
            features.append(f)
            fail = f['err'] is not None
            counts['nonvote'] += 1
            counts['failed'] += int(fail)
            counts['fee_sol'] += f['fee_sol']
            counts['failed_fee_sol'] += f['fee_sol'] * fail
            fees.append(f['fee_sol'])
            for p in f['top_programs']:
                programs[p]['total'] += 1
                programs[p]['failed'] += int(fail)
                programs[p]['fee_sol'] += f['fee_sol']
                programs[p]['cu'] += f['cu']
            payers[f['payer']]['total'] += 1
            payers[f['payer']]['failed'] += int(fail)
            payers[f['payer']]['fee_sol'] += f['fee_sol']
            bucket = (b['blockTime'] - m['start_ts']) // 600
            bins[bucket]['nonvote'] += 1
            bins[bucket]['failed'] += int(fail)
    save('features.json.gz', features)
    ranked = {}
    for metric in ['max_sol_change','max_stable_change','fee_sol']:
        eligible = features if metric=='fee_sol' else [f for f in features if f['err'] is None]
        ranked[metric] = sorted(eligible, key=lambda f:f[metric], reverse=True)[:30]
    ranked['special_events'] = [f for f in features if f['err'] is None and any('liquidat' in s.lower() or 'flash' in s.lower() for s in f['events'])][:80]
    save('candidates.json', ranked)
    summary = {'window':{k:m[k] for k in ['start_utc','end_utc','start_slot','end_slot','produced_blocks','sampling']},'counts':dict(counts),'fee_median_sol':statistics.median(fees),'fee_p95_sol':sorted(fees)[int(len(fees)*.95)],'fee_p99_sol':sorted(fees)[int(len(fees)*.99)],'programs':sorted([{'program':k,**v} for k,v in programs.items()],key=lambda x:x['total'],reverse=True),'payers':sorted([{'payer':k,**v} for k,v in payers.items()],key=lambda x:x['total'],reverse=True)[:40],'ten_minute_bins':dict(bins)}
    save('summary.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['programs','payers']},indent=2))
    for metric, rows in ranked.items():
        print(metric)
        for f in rows[:10]:
            print(json.dumps({k:f[k] for k in ['signature','slot','time','payer','err','fee_sol','max_sol_change','max_stable_change','top_programs','events']}))

if __name__ == '__main__':
    {'collect':collect,'analyze':analyze}[sys.argv[1]]()
