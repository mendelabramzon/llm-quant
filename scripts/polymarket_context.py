"""Read primary, public market metadata for observed outcome token IDs."""
import collections
import gzip
import json
import urllib.request
import urllib.error
from onchain_probe import ROOT, save, utc

out = ROOT / 'research/2026-09-05/followup'
with gzip.open(ROOT / 'research/2026-09-05/analysis/events.jsonl.gz', 'rt') as f:
    events = [json.loads(l) for l in f if 'OrderFilled' in l]
events = [e for e in events if e['chain'] == 'polygon' and e['emitter'] in
          ['0xe111180000d2663c0091e4f400237545b87b996b', '0xe2222d279d744050d28e00520010520000310f59']]
selected = collections.Counter(e['token_id'] for e in events).most_common(3)
result = []
for token, count in selected:
    path = out / ('market_' + token + '.json')
    url = 'https://gamma-api.polymarket.com/markets?clob_token_ids=' + token
    if path.exists():
        raw = json.loads(path.read_text())
    else:
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                raw = json.load(response)
        except urllib.error.HTTPError as exc:
            result.append({'observed_at': utc(), 'source_url': url, 'token_id': token,
                           'error': 'HTTP ' + str(exc.code), 'question': None})
            continue
        save(path, raw)
    matches = [m for m in raw if token in str(m.get('clobTokenIds', ''))]
    for m in matches:
        ids = json.loads(m['clobTokenIds']) if isinstance(m['clobTokenIds'], str) else m['clobTokenIds']
        outcomes = json.loads(m['outcomes']) if isinstance(m['outcomes'], str) else m['outcomes']
        result.append({'observed_at': utc(), 'source_url': url, 'token_id': token, 'order_fill_events': count,
                       'question': m['question'], 'slug': m['slug'], 'condition_id': m.get('conditionId'),
                       'outcome': outcomes[ids.index(token)], 'end_date': m.get('endDate'),
                       'description': m.get('description'),
                       'metadata_timing': 'Fetched after the onchain sample; not a historical metadata snapshot.'})
save(out / 'market_context.json', result)
print(json.dumps(result, indent=2))
