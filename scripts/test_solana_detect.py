"""Tests for the Solana detector set and the window diff, on synthetic analysis/head fixtures.

Each test pins one property that a wrong detector would silently violate: thresholds are respected, keys are stable
across windows (the whole point of a ledger), a broken detector is reported rather than dropped, and the diff treats
missing metrics as unknown rather than as zero.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import solana_detect as sd  # noqa: E402

SOL = sd.SOL
USDC = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
JITOSOL = [m for m, v in sd.MINTS.items() if v['symbol'] == 'jitoSOL'][0]


def analysis(**over):
    A = {
        'window': {'start_utc': '2026-09-10T16:55:43+00:00', 'end_utc': '2026-09-10T17:55:43+00:00', 'start_slot': 1, 'end_slot': 2,
                   'skipped_slots': 3, 'hours': 1.0},
        'price_basis': {'sol_usd_median': 100.0},
        'network': {'nonvote': 1_000_000, 'failed': 300_000, 'tps_nonvote': 278.0, 'failed_share': 0.3, 'fees_sol': 200.0,
                    'priority_fees_sol': 170.0, 'failed_fees_sol': 50.0},
        'kinds': [{'kind': 'swap', 'share': 0.16}, {'kind': 'transfer', 'share': 0.09}],
        'programs': [
            {'program': 'Quote1', 'label': 'Quoter', 'kind': 'dex', 'tx': 60_000, 'failed': 10_000, 'fail_share': 0.17, 'fee_sol': 1.0,
             'unique_payers': 3, 'top_payer': 'p', 'top_payer_share': 0.9, 'token_move_share': 0.001},
            {'program': 'Retail1', 'label': 'Retail', 'kind': 'dex', 'tx': 900_000, 'failed': 90_000, 'fail_share': 0.1, 'fee_sol': 40.0,
             'unique_payers': 150_000, 'top_payer': 'p', 'top_payer_share': 0.01, 'token_move_share': 0.9},
            {'program': 'Spam1', 'label': None, 'kind': 'bot', 'tx': 30_000, 'failed': 29_000, 'fail_share': 0.967, 'fee_sol': 0.3,
             'unique_payers': 4, 'top_payer': 'p', 'top_payer_share': 0.5, 'token_move_share': 0.0},
            {'program': 'Small', 'label': None, 'kind': 'bot', 'tx': 5_000, 'failed': 5_000, 'fail_share': 1.0, 'fee_sol': 0.05,
             'unique_payers': 1, 'top_payer': 'p', 'top_payer_share': 1.0, 'token_move_share': 0.0},
        ],
        'dex': {'total_priced_usd': 200e6, 'volume_by_venue': [{'venue': 'Pump.fun Amm', 'usd': 140e6, 'swaps': 1}],
                'self_matched': {'total_usd': 80e6, 'swaps': 90_000, 'wallet_pairs': 8_000,
                                 'by_venue': [{'venue': 'Pump.fun Amm', 'usd': 80e6, 'swaps': 90_000, 'share_of_venue': 0.57},
                                              {'venue': 'Orca', 'usd': 2e6, 'swaps': 10, 'share_of_venue': 0.01}],
                                 'by_token': [{'mint': 'MintA', 'symbol': None, 'usd': 12e6, 'swaps': 9_000},
                                              {'mint': 'MintB', 'symbol': None, 'usd': 0.5e6, 'swaps': 900}]},
                'sandwiches': {'n': 700}, 'top_pairs': [{'venue': 'Pump.fun Amm', 'pair': 'MintA / SOL', 'usd': 12e6, 'swaps': 1}]},
        'launches': {'total': 1_700, 'unique_creators': 800, 'top_creators': [['Fact1', 60], ['Fact2', 19]], 'by_program': []},
        'pump': {'sol': {'bonding_curve_sol': 40_000.0}, 'cashback_sol_received': 700.0, 'counts': {'pumpswap_pools_created': 200}},
        'lending': {'n_liquidations': 0, 'liquidation_attempts': {'Kamino Lend': {'ok': 0, 'failed': 184}},
                    'events': {'Kamino Lend': {'tx': 4_000, 'failed': 2_500, 'flash_borrow_reserve_liquidity (failed)': 2_384}},
                    'flash_payers': {'Kamino Lend': [['guof (failed)', 2_091], ['ok1', 18], ['few (failed)', 8]]}},
        'issuance': {'by_mint': {'USDC': {'net': -4.8e6}}},
        'cctp': {'out_total': 2.4e6, 'in_total': 2.3e6, 'out_by_chain': [{'chain': 'Ethereum', 'usd': 1.9e6, 'n': 12},
                                                                         {'chain': 'domain 27', 'usd': 20_523, 'n': 33}], 'in_by_chain': []},
        'exchanges': {'net_flow': {'Binance': {'usd_net': 5.7e6, 'txs': 1_900, 'usd': {'USDC': 5.5e6, 'SOL': -2.4e6}},
                                   'OKX': {'usd_net': -1e6, 'txs': 100, 'usd': {}}},
                      'unlabelled_fan_in': [{'address': 'Hub1', 'label': None, 'unique_senders': 2_348, 'sol_received': 9_739.1, 'median_sol': 0.5,
                                             'out_transfers': 60, 'out_destinations': '1'},
                                            {'address': 'Hub2', 'label': None, 'unique_senders': 120, 'sol_received': 50.0, 'median_sol': 0.4,
                                             'out_transfers': 1, 'out_destinations': '1'}],
                      'distributors': [{'address': 'Dist1', 'label': None, 'out_transfers': 3_220, 'sol_sent': 14_665.9, 'destinations': '6+'}]},
        'large': {'moves': [{'owner': 'Big1', 'label': None, 'asset': 'USDC', 'delta': -10e6, 'usd': 10e6, 'kind': 'protocol', 'sig': 's', 'slot': 1,
                             'time': 't', 'payer': 'p', 'programs': []},
                            {'owner': 'Big1', 'label': None, 'asset': 'USDC', 'delta': 9e6, 'usd': 9e6, 'kind': 'protocol', 'sig': 's2', 'slot': 2,
                             'time': 't', 'payer': 'p', 'programs': []}]},
        'poisoning': {'dust_senders': [{'sender': 'Dust1', 'dust_transfers': 7_180, 'recipients': 866},
                                       {'sender': 'Dust2', 'dust_transfers': 400, 'recipients': 300}]},
        'payers': [{'payer': 'P1'}], 'top_fee_payers': [{'payer': 'F1'}],
        'jito': {'tips_sol': 36.4, 'by_tip_account': [
            {'account': '96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5', 'tips_sol': 30.0, 'unique_payers': 300},
            {'account': 'DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL', 'tips_sol': 4.0, 'unique_payers': 200},
            {'account': '4ACfpUFoaSD9bfPdeu6DBt89gB6ENTeHBXCAi87NhDEE', 'tips_sol': 2.0, 'unique_payers': 150},
            {'account': 'astra4uejePWneqNaJKuFFA8oonqCE1sqF6b45kDMZm', 'tips_sol': 0.4, 'unique_payers': 50},
            {'account': 'Unknown111', 'tips_sol': 0.0, 'unique_payers': 0}]},
        'leaders': {'n_leaders': 446},
    }
    A.update(over)
    return A


def head(**over):
    H = {
        'epoch': {'epoch': 1031},
        'jupiter_prices': {SOL: {'usdPrice': 100.0}, JITOSOL: {'usdPrice': 130.65}},
        'stake_pool_nav': {'jitoSOL': {'nav_sol': 1.3000, 'last_update_epoch': 1030}},
        'kamino_markets': [{'name': 'Main Market', 'reserves': [{'token': 'USDC', 'supply_apy': 0.045, 'supplied_usd': 300e6},
                                                                 {'token': 'USDT', 'supply_apy': 0.02, 'supplied_usd': 0.5e6}]}],
        'save_main': [{'symbol': 'USDC', 'supply_apy': 0.0296, 'supplied_usd': 22e6},
                      {'symbol': 'USDT', 'supply_apy': 0.06, 'supplied_usd': 5e6}],
        'jupiter_lend': [{'asset_symbol': 'USDC', 'supply_rate_bps': 456, 'total_assets': 450e6, 'asset_price': 1.0}],
    }
    H.update(over)
    return H


def ctx_for(tmp_path, A=None, H=None):
    out = tmp_path / 'w'
    out.mkdir()
    (out / 'analysis.json').write_text(json.dumps(A or analysis()))
    if H is not None:
        (out / 'head_state.json').write_text(json.dumps(H))
    return sd.Context(out)


def keys(hits):
    return sorted(h.identity() for h in hits)


def test_wash_volume_thresholds(tmp_path):
    hits = sd.wash_volume(ctx_for(tmp_path))
    ids = keys(hits)
    assert 'sol_wash_volume:all' in ids
    assert 'sol_wash_volume:venue:Pump.fun Amm' in ids
    assert 'sol_wash_volume:venue:Orca' not in ids          # $2M but only 1% of the venue
    assert not any(i.startswith('sol_wash_volume:mint:') for i in ids)   # tokens are evidence, not ledger rows
    venue = [h for h in hits if h.key == 'venue:Pump.fun Amm'][0]
    assert [t['mint'] for t in venue.evidence['top_tokens']] == ['MintA']  # MintB is below WASH_MIN_USD
    top = [h for h in hits if h.key == 'all'][0]
    assert abs(top.evidence['share'] - 0.4) < 1e-9 and top.usd == 80e6


def test_quote_poster_and_failure_spam_are_disjoint_lenses(tmp_path):
    ctx = ctx_for(tmp_path)
    q = keys(sd.quote_posters(ctx))
    assert q == ['sol_quote_poster:Quote1', 'sol_quote_poster:all']   # Spam1 moves no token but is under QUOTE_MIN_TX
    agg = [h for h in sd.quote_posters(ctx) if h.key == 'all'][0]
    assert agg.evidence['tx'] == 60_000 and abs(agg.evidence['tx'] / agg.evidence['nonvote'] - 0.06) < 1e-9
    f = keys(sd.failure_spam(ctx))
    assert f == ['sol_failure_spam:Spam1', 'sol_failure_spam:all']   # Small is 100% failed but under SPAM_MIN_TX
    aggf = [h for h in sd.failure_spam(ctx) if h.key == 'all'][0]
    assert aggf.evidence['failed'] == 29_000 and aggf.evidence['fee_usd'] == 30


def test_hubs_factories_flash_and_dust(tmp_path):
    ctx = ctx_for(tmp_path)
    assert keys(sd.collector_hubs(ctx)) == ['sol_collector_hub:all', 'sol_collector_hub:in:Hub1', 'sol_collector_hub:out:Dist1']
    agg, hub = sd.collector_hubs(ctx)[:2]
    assert hub.severity == 'notable' and abs(hub.usd - 973_910) < 1
    assert agg.evidence['hubs'] == ['Hub1'] and agg.evidence['distributors'] == ['Dist1']
    assert keys(sd.launch_factories(ctx)) == ['sol_launch_factory:Fact1', 'sol_launch_factory:all']
    assert keys(sd.flash_loan_spam(ctx)) == ['sol_flash_loan_spam:Kamino Lend:guof']
    assert keys(sd.liquidation_drought(ctx)) == ['sol_liquidation_drought:all']
    assert keys(sd.dust_poisoning(ctx)) == ['sol_dust_poisoning:Dust1']
    assert keys(sd.exchange_flow(ctx)) == ['sol_exchange_flow:Binance']
    assert keys(sd.cctp_unknown_domain(ctx)) == ['sol_cctp_unknown_domain:out:domain 27']
    assert keys(sd.large_moves(ctx)) == ['sol_large_move:Big1']   # one row per owner, largest first


def test_liquidations_present_means_no_drought(tmp_path):
    A = analysis()
    A['lending']['n_liquidations'] = 3
    assert sd.liquidation_drought(ctx_for(tmp_path, A)) == []


def test_lst_nav_basis_uses_onchain_nav_and_sol_price(tmp_path):
    ctx = ctx_for(tmp_path, H=head())
    hits = sd.lst_nav_basis(ctx)
    assert keys(hits) == ['sol_lst_nav_basis:jitoSOL']
    assert abs(hits[0].evidence['basis_bp'] - 50.0) < 0.2       # 1.3065 / 1.3000 - 1 = +50 bp
    H = head(jupiter_prices={SOL: {'usdPrice': 100.0}, JITOSOL: {'usdPrice': 130.1}})   # +8 bp: below threshold
    assert sd.lst_nav_basis(ctx_for(tmp_path / 'b', H=H) if (tmp_path / 'b').mkdir() is None else None) == []


def test_stable_rate_gap_needs_size_on_both_sides(tmp_path):
    hits = sd.stable_rate_gap(ctx_for(tmp_path, H=head()))
    ids = keys(hits)
    # USDC: Jupiter Lend 4.56% vs Save 2.96% = 1.60pp on $22M+; Kamino at 4.5% is neither extreme.
    assert ids == ['sol_stable_rate_gap:USDC:Jupiter Lend/Save main']
    h = hits[0]
    assert abs(h.evidence['gap_pp'] - 1.6) < 1e-6 and h.economics['capacity_usd'] == 22_000_000
    assert abs(h.usd - 22e6 * 0.016) < 1
    # USDT: Save 6% vs Kamino 2% is 4pp, but Kamino holds $0.5M < RATE_MIN_SUPPLIED_USD, so no pair qualifies.
    assert not any('USDT' in i for i in ids)


def test_no_head_state_means_no_head_detectors_and_no_error(tmp_path):
    ctx = ctx_for(tmp_path)
    hits, meta = sd.run_all(ctx)
    assert not any(m['error'] for m in meta)
    assert all(m['hits'] == 0 for m in meta if m['detector'] in ('sol_lst_nav_basis', 'sol_stable_rate_gap'))
    assert hits[0].severity == 'notable' and hits[0].usd == 80e6     # sorted: notable first, then by usd


def test_broken_detector_is_reported_not_dropped(tmp_path, monkeypatch):
    def boom(ctx):
        raise KeyError('missing')
    monkeypatch.setattr(sd, 'DETECTORS', sd.DETECTORS + [('sol_boom', 'x', boom)])
    _, meta = sd.run_all(ctx_for(tmp_path))
    m = [m for m in meta if m['detector'] == 'sol_boom'][0]
    assert m['error'].startswith('KeyError') and m['hits'] == 0


def test_keys_are_stable_across_windows(tmp_path):
    a = ctx_for(tmp_path / 'a' if (tmp_path / 'a').mkdir() is None else None)
    B = analysis()
    B['dex']['self_matched']['total_usd'] = 10e6   # numbers change, identity does not
    B['dex']['self_matched']['by_venue'][0]['usd'] = 10e6
    (tmp_path / 'b').mkdir()
    b = ctx_for(tmp_path / 'b', B)
    ha, _ = sd.run_all(a)
    hb, _ = sd.run_all(b)
    assert keys(ha) == keys(hb)
    assert [h.title for h in ha] != [h.title for h in hb]


def test_diff_metrics_and_actors():
    prev, cur = analysis(), analysis()
    cur['network']['tps_nonvote'] = 556.0
    del cur['jito']                                  # a metric absent on one side is unknown, not zero
    cur['programs'] = [dict(p) for p in prev['programs']]
    cur['programs'][0]['tx'] = 120_000               # doubled -> "moved"
    cur['programs'].append({'program': 'New1', 'label': 'Newcomer', 'kind': 'dex', 'tx': 70_000})
    cur['dex']['self_matched']['by_token'] = [{'mint': 'MintA', 'usd': 1, 'swaps': 1}, {'mint': 'MintZ', 'usd': 1, 'swaps': 1}]
    D = sd.compute_diff(prev, cur)
    m = {r['metric']: r for r in D['metrics']}
    assert m['non-vote TPS']['delta'] == 1.0
    tips = m['tips paid to tip accounts, all providers (successful txs)']
    assert tips['cur'] is None and tips['delta'] is None
    assert abs(m['wash share of priced volume']['cur'] - 0.4) < 1e-9
    assert [r['program'] for r in D['programs']['entered']] == ['New1']
    assert D['programs']['left'] == []
    assert [r['program'] for r in D['programs']['moved']] == ['Quote1'] and D['programs']['moved'][0]['delta'] == 1.0
    assert D['actors']['wash_tokens']['persisting'] == ['MintA']
    assert D['actors']['launch_creators']['persisting'] == ['Fact1', 'Fact2']
    md = sd.render_diff(D, 'p', 'c')
    assert '| non-vote TPS | 278 | 556 | +100% |' in md
    assert 'Newcomer (dex, 70,000 txs)' in md
    assert 'Partial window' not in md and D['coverage'] == {'prev': None, 'cur': None}   # fixture windows carry no slot counts


def test_diff_marks_partial_window_totals():
    prev, cur = analysis(), analysis()
    prev['window'].update(produced_slots=11_000, blocks_analyzed=11_000)
    cur['window'].update(produced_slots=11_000, blocks_analyzed=1_100)
    cur['network']['fees_sol'] = 20.0
    D = sd.compute_diff(prev, cur)
    assert D['coverage']['cur'] == 0.1
    md = sd.render_diff(D, 'p', 'c')
    assert 'cur analysed 10.0% of its produced slots' in md
    assert '| non-vote fees | ~200.0 | ~20.0 | ~-90% |' in md      # a total: marked
    assert '| non-vote TPS | 278 | 278 | +0% |' in md               # a rate: not marked


def test_tip_providers_group_accounts_by_label(tmp_path):
    hits = sd.tip_providers(ctx_for(tmp_path))
    assert [h.key for h in hits] == ['Jito', 'Helius Sender', 'Astralane']     # zero-tip accounts are dropped
    jito = hits[0]
    assert jito.evidence['accounts'] == 2 and abs(jito.evidence['tips_sol'] - 34.0) < 1e-9
    assert abs(jito.evidence['share'] - 34.0 / 36.4) < 1e-4 and abs(jito.usd - 3400.0) < 1e-6
