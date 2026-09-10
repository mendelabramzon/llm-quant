"""Cross-artifact checks and an independent raw calldata/log check of the report's LPT cohort."""
import collections,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from window_raw import Window,TRANSFER,word,hx,topic_addr

def read(n):return json.loads((OUT/(n+'.json')).read_text())
v,a,d,f,m,h=map(read,['verify','analysis','detectors','fee_census','manifest','head_state'])
assert v['all_ok'] and not v['claims']['dangling']
assert m['complete'] and not m['quality_issues'] and not m['hash_recheck']['mismatches']
assert f['sample_complete'] and f['blocks']==373 and f['transactions']==113684
assert f['window_gas_used']==sum(x['gas_used'] for x in read('blocks_manifest')['blocks'])
assert len(d['detectors'])==17 and not any(x['error'] for x in d['detectors'])
assert not any(x['detector']=='liquidity_blackout' and x['key']=='Aave v3:PYUSD' for x in d['hits'])
for x in d['hits']:
 if x['detector']=='rate_dispersion' and x.get('economics',{}).get('go'):
  assert x['economics']['size_usd']<=x['evidence']['source_available_usd']
 if x['detector']=='nav_discount' and x['key']=='rETH':
  assert not x['economics']['go'] and x['economics']['net_per_year_usd']==0
bf=read('borrower_followup')
assert all(x['reconciles'] for x in bf['accounts']) and bf['block']==h['block']==m['last_block']
lf=read('liquidity_followup')
assert lf['reth']['collateral_eth']<1e-7
for row in lf['pyusd']:
 assert row['cash_pyusd']>896000 and row['end_borrow_apr']<.05
 if row['updates']:
  assert row['updates'][0]['borrow_apr']>.3
  assert row['updates'][-1]['borrow_apr']==row['end_borrow_apr']
fan=next(x['evidence'] for x in d['hits'] if x['detector']=='token_fan_in')
token,sink=fan['token'],fan['recipient']
count,total,after=0,0,0
senders,txids=set(),set()
buckets=collections.Counter(); amounts=[]
for b,logs in Window(OUT).blocks():
 calls={t['hash']:t for t in b['transactions'] if (t.get('to') or '').lower()==token}
 for l in logs:
  topics=l.get('topics',[])
  if l['address'].lower()!=token or len(topics)!=3 or topics[0]!=TRANSFER or topic_addr(topics[2])!=sink:continue
  amount=word(l['data'],0)
  if amount<=0:continue
  sender=topic_addr(topics[1]); t=calls[l['transactionHash']]
  assert t['from'].lower()==sender
  assert t['input'][:10]=='0xa9059cbb'
  args='0x'+t['input'][10:]
  assert '0x'+args[2:66][-40:].lower()==sink and word(args,1)==amount
  count+=1;total+=amount;senders.add(sender);txids.add(t['hash']);amounts.append(amount)
  ts=hx(b['timestamp']);buckets[str(ts//900*900)]+=1
  after+=datetime.fromtimestamp(ts,timezone.utc).strftime('%H:%M')>='08:30'
assert count==len(senders)==len(txids)==fan['transfers']==72446
assert str(total)==fan['total_raw'] and dict(buckets)==fan['buckets'] and after==72443
cohort=read('lpt_consolidation')
assert cohort['settled_transfers']==count and cohort['unique_senders']==len(senders)
assert abs(cohort['token_units']-total/1e18)<1e-8
broken=[]
for name in ('insights.md','method.md','report.md'):
 p=OUT/name
 assert p.exists(),name
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if target != 'validation.json' and '://' not in target and not target.startswith('#') and not (p.parent/target.split('#')[0]).exists():broken.append((name,target))
assert not broken,broken
suite=(OUT/'tests.log').read_text()
assert 'Ran 174 tests' in suite and 'OK (skipped=2)' in suite
files=[ROOT/'scripts/live_scan.py',ROOT/'scripts/detectors/rate_dispersion.py',ROOT/'scripts/detectors/token_fan_in.py',
       ROOT/'scripts/detectors/liquidity_blackout.py',ROOT/'scripts/detectors/nav_discount.py',ROOT/'scripts/detectors/run.py']
result={'validated_at':datetime.now(timezone.utc).isoformat(),'window':a['window'],'all_ok':True,
 'raw_complete':m['complete'],'hash_recheck':m['hash_recheck'],
 'aggregate_checks':len(v['checks']),'identity_groups':len(v['identities']),
 'receipt_blocks':f['blocks'],'receipt_transactions':f['transactions'],'receipt_checks':f['receipt_checks'],
 'detectors':len(d['detectors']),'hits':len(d['hits']),'detector_errors':0,
 'source_cap_checks':'all positive rate-switch sizes <= measured source availability',
 'borrower_reconciliations':len(bf['accounts']),'health_positions':len(h['health']),
 'pyusd_false_blackout_removed':True,'reth_conditional_quote_rejected':True,
 'lpt_raw_log_and_calldata_check':{'transfers':count,'distinct_senders':len(senders),'distinct_transactions':len(txids),
  'raw_amount':str(total),'after_0830':after,'all_window_tx_share':count/a['window']['transactions']},
 'unit_tests':{'run':174,'passed':172,'skipped':2,'failures':0},'local_links_ok':True,
 'claim_audit':v['claims'],
 'code_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(OUT/'validation.json').write_text(json.dumps(result,indent=1)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('claim_audit','code_sha256')},indent=1))
