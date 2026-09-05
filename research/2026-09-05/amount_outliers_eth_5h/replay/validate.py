"""Offline consistency and interpretation regressions for the pinned five-hour study."""
import collections
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import unittest

import tx_types as T


def main():
    out = T.OUT_DEFAULT
    read = lambda name: json.loads((out / name).read_text())
    manifest = json.loads((T.DAY / 'manifest.json').read_text())
    stats, classified = read('stats.json'), read('classified.json')
    rows, profiles = T.load_big(out), T.load_profiles(out)
    with gzip.open(out / 'types_by_hash.json.gz', 'rt') as f:
        labels = json.load(f)
    with gzip.open(out / 'investigations.jsonl.gz', 'rt') as f:
        investigations = [json.loads(line) for line in f]
    checks = {}

    def check(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)

    check('ethereum_mainnet', manifest['chain_id'] == 1 and manifest['chain'] == 'ethereum')
    check('five_hours', manifest['end_timestamp'] - manifest['start_timestamp'] == 18000)
    check('collection_verified', manifest['complete'] and not manifest['quality_issues'])
    check('canonical_hash_sample', manifest['hash_recheck']['sampled'] == 16 and not manifest['hash_recheck']['mismatches'])
    check('raw_census_totals', all(manifest[k] == stats['counts'][k] for k in ('blocks', 'transactions', 'logs')))
    hashes = {r['h'] for r in rows}
    check('candidate_and_label_counts', len(hashes) == len(rows) == stats['above_threshold'] == len(labels) == len(investigations))
    check('all_investigations_present', hashes == set(labels) == {r['hash'] for r in investigations})
    check('candidate_statuses', all(r['status'] in ('success', 'success_from_logs') for r in rows))
    check('selection_recomputes', all(r['selection'] == [k for k, n in (('pc', 10000), ('flash_usd', 10000), ('gross', 100000)) if Decimal(r[k]) >= n] for r in rows))
    check('primary_labels_replay', all(T.classify_row(r, profiles, Decimal(10000))[0] == labels[r['h']] for r in rows))
    check('no_rule_errors', not classified['rule_errors'] and all(not r.get('rule_errors') for r in rows))
    check('zero_not_a_holder', all(n[0] != T.ZERO for r in rows for n in r['net']))
    check('all_five_hour_buckets', all(len(t['investigation']['hourly']) == 5 and sum(t['investigation']['hourly']) == t['transactions'] for t in classified['types'] if t['transactions']))
    check('group_totals', sum(g['transactions'] for g in classified['groups']) == len(rows))
    check('usd_totals', sum(Decimal(r['pc']) for r in rows) == Decimal(classified['coverage']['sum_usd']) == sum(Decimal(g['sum_usd']) for g in classified['groups']))
    residue = read('residue.json')['clusters']
    check('all_unknown_clusters_retained', sum(c['transactions'] for c in residue) == classified['coverage']['unknown'])
    prices = read('prices.json')
    check('verified_decimals', all(prices['registry_validation'].get(a, {}).get('decimals_match') for a in T.ASSETS))
    check('five_hour_prices', all(len(prices['hourly'][asset]) == 5 for asset in ('ETH', 'BTC')))
    check('no_implied_prices', not stats['implied_prices'])
    receipts = read('native_status.json')
    check('native_receipts_success', len(receipts) == 1416 and all(r['status'] == 'success' for r in receipts.values()))
    ctx, packets = read('context.json'), read('packets.json')
    check('packet_receipts_success', all(ctx['receipts'].get(p['transaction']['hash'], {}).get('status_ok') for p in packets))
    expected = {
        '0x84421f1ca5d985b7c4fdd57e4d20fb947bdb8ad9aaaf99833e2e29b8ff5d3655': 'unknown',
        '0xfcb06a2e24b43beadff24dca822a2e9f6abfb58f74faf45ab7e7df3410a7addd': 'bridge_out',
        '0xb48219e059fd1c60de893fbae1583b71909dd380b4a35fa8d2581a2acd9ecb58': 'cow_settlement',
        '0x90c68d21460c9752b8bbe536a8e052627b0069c71299cc908d177288d28891df': 'lending_with_swap',
        '0xaef5aedfe316784db2413644b75ab893babaaa40dee154bd7e2fbb4430304749': 'flash_funded_lending',
        '0xfb3c8db76ae820d5b0f9478c3f381318f93c1ce0a0e0000fb7d261e568cd4bb5': 'liquidity_collect_only',
        '0x0fff7095c88bae0c4fc9ee2d14038b803e17f36c349dcde31cb9c9ab6cbd62f8': 'operator_token_batch',
        '0xfec01dde6895fad8be1546bfbb88bf41ba3a2a3ee45c6e853af05814e60faa40': 'contract_token_execution',
        '0xbfab93a1d6f770012c597a6e9d20cd515028da66f9db0733b36c717156689519': 'dolomite_account_deposit',
    }
    check('interpretation_regressions', all(labels[h] == t for h, t in expected.items()))
    dolo = next(t for t in classified['types'] if t['id'] == 'dolomite_account_deposit')['investigation']
    check('signed_account_states', dolo['resulting_account_states'] == {'positive_balance': 4, 'debt_remaining': 1, 'zero_balance': 1})
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern='test_tx_types.py')
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    check('regression_unit_tests', result.wasSuccessful())
    notes = T.parse_notes(out / 'qual_notes.md')
    check('all_packets_have_review_notes', all(p['transaction']['hash'] in notes for p in packets))
    artifact = {'checks': checks, 'checks_passed': len(checks), 'unit_tests': result.testsRun,
                'known_case_regressions': expected, 'coverage': classified['coverage'],
                'scope': {'start': manifest['start_utc'], 'end_exclusive': manifest['end_utc']},
                'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},
                'interpretation': 'Consistency checks and targeted regressions; not independent classification-accuracy measurement.'}
    T.save(out / 'validation.json', artifact)
    print(json.dumps({'checks_passed': len(checks), 'unit_tests': result.testsRun, 'coverage': classified['coverage']}, indent=2))


if __name__ == '__main__':
    main()
