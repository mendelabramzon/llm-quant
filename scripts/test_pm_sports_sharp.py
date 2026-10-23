"""Tests for the money-deciding pure functions of pm_sports_sharp: de-vigging, odds availability, fees, fill rules,
signal selection and team-name matching."""
import datetime as dt
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_sports_sharp as S  # noqa: E402

LON = S.LONDON


def ts(y, m, d, hh=0, mm=0, tz=LON):
    return dt.datetime(y, m, d, hh, mm, tzinfo=tz).timestamp()


class TestDevig:
    def test_implied_rejects_missing_or_bad(self):
        assert S.implied([2.0, None, 3.0]) is None
        assert S.implied([1.0, 2.0, 3.0]) is None
        assert S.implied([]) is None

    def test_multiplicative_sums_to_one_and_keeps_ratios(self):
        p = S.devig_mult([2.0, 3.5, 4.0])
        assert abs(sum(p) - 1.0) < 1e-12
        raw = [1 / 2.0, 1 / 3.5, 1 / 4.0]
        assert abs(p[0] / p[2] - raw[0] / raw[2]) < 1e-12

    def test_shin_sums_to_one(self):
        for odds in ([1.3, 6.0, 8.5], [2.25, 3.5, 2.9], [1.05, 15.0, 41.0], [1.9, 1.9]):
            p = S.devig_shin(odds)
            assert abs(sum(p) - 1.0) < 1e-9

    def test_shin_takes_more_from_longshots(self):
        odds = [1.25, 6.0, 11.0]          # ~6.6% overround
        pm, ps = S.devig_mult(odds), S.devig_shin(odds)
        assert ps[2] < pm[2]              # the longshot is shaded down
        assert ps[0] > pm[0]              # the favourite gets the difference

    def test_shin_symmetric_two_way_is_half(self):
        p = S.devig_shin([1.9, 1.9])
        assert abs(p[0] - 0.5) < 1e-9

    def test_no_overround_is_normalised(self):
        p = S.devig_shin([2.0, 2.0])
        assert p == [0.5, 0.5]

    def test_devig_dispatch(self):
        assert S.devig([2.0, 3.5, 4.0], 'mult') == S.devig_mult([2.0, 3.5, 4.0])
        assert S.devig([2.0, 3.5, 4.0], 'shin') == S.devig_shin([2.0, 3.5, 4.0])


class TestFootballData:
    def test_fd_odds_prefers_pinnacle_then_average(self):
        row = {'PSH': '2.0', 'PSD': '3.4', 'PSA': '4.0', 'AvgH': '1.9', 'AvgD': '3.3', 'AvgA': '3.9'}
        assert S.fd_odds(row, 'pre') == ('pinnacle', [2.0, 3.4, 4.0])
        row2 = dict(row, PSD='')
        assert S.fd_odds(row2, 'pre') == ('average', [1.9, 3.3, 3.9])
        assert S.fd_odds({}, 'pre') == (None, None)

    def test_fd_odds_closing_columns(self):
        row = {'PSCH': '2.1', 'PSCD': '3.3', 'PSCA': '3.8', 'PSH': '9', 'PSD': '9', 'PSA': '9'}
        assert S.fd_odds(row, 'close') == ('pinnacle', [2.1, 3.3, 3.8])

    def test_fd_kickoff_is_london_time(self):
        # 15/08/2025 20:00 BST = 19:00 UTC; 06/12/2025 15:00 GMT = 15:00 UTC
        assert S.fd_kickoff('15/08/2025', '20:00') == ts(2025, 8, 15, 19, 0, dt.timezone.utc)
        assert S.fd_kickoff('06/12/2025', '15:00') == ts(2025, 12, 6, 15, 0, dt.timezone.utc)
        assert S.fd_kickoff('06/12/25', '15:00') == ts(2025, 12, 6, 15, 0, dt.timezone.utc)
        assert S.fd_kickoff('bad', '15:00') is None

    def test_available_saturday_uses_friday_1800(self):
        ko = ts(2025, 12, 6, 15, 0)                      # Saturday
        assert S.fd_available(ko) == ts(2025, 12, 5, 18, 0)

    def test_available_monday_uses_friday(self):
        ko = ts(2025, 12, 8, 20, 0)                      # Monday
        assert S.fd_available(ko) == ts(2025, 12, 5, 18, 0)

    def test_available_wednesday_uses_tuesday(self):
        ko = ts(2025, 12, 3, 19, 30)                     # Wednesday
        assert S.fd_available(ko) == ts(2025, 12, 2, 18, 0)

    def test_available_friday_evening_same_day(self):
        ko = ts(2025, 12, 5, 20, 0)                      # Friday 20:00
        assert S.fd_available(ko) == ts(2025, 12, 5, 18, 0)

    def test_available_friday_afternoon_blocks_decisions(self):
        ko = ts(2025, 12, 5, 15, 0)                      # Friday 15:00: odds taken that afternoon, time unknown
        assert S.fd_available(ko) == ko

    def test_available_tuesday_evening(self):
        ko = ts(2025, 12, 2, 19, 45)
        assert S.fd_available(ko) == ts(2025, 12, 2, 18, 0)


class TestNames:
    def test_aliases(self):
        assert S.team_sim('Manchester United FC', 'Man United') == 1.0
        assert S.team_sim('Nottingham Forest FC', "Nott'm Forest") == 1.0
        assert S.team_sim('Sporting CP', 'Sp Lisbon') == 1.0
        assert S.team_sim('Stade Rennais FC 1901', 'Rennes') == 1.0
        assert S.team_sim('Wolverhampton Wanderers FC', 'Wolves') == 1.0

    def test_transliteration(self):
        assert S.team_sim('FC Nordsjælland', 'Nordsjaelland') == 1.0
        assert S.team_sim('Brøndby IF', 'Brondby') == 1.0
        assert S.team_sim('Kasımpaşa SK', 'Kasimpasa') == 1.0

    def test_edit_distance(self):
        assert S.edit_distance('levadiakos', 'levadeiakos') == 1
        assert S.edit_distance('panaitolikos', 'panetolikos') == 2
        assert S.team_sim('APO Levadiakos FC', 'Levadeiakos') == 1.0

    def test_distinct_clubs_do_not_match(self):
        assert S.team_sim('Manchester City FC', 'Man United') < 1.0
        assert S.team_sim('Real Madrid CF', 'Sociedad') < 0.5          # 'real' alone is generic
        assert S.team_sim('Real Sociedad de Fútbol', 'Sociedad') == 1.0

    def test_pair_orientation(self):
        sc, sw, a, b = S.pair_score('Arsenal FC', 'Coventry City FC', 'Coventry', 'Arsenal')
        assert sw is True and a == 1.0 and b == 1.0
        sc, sw, a, b = S.pair_score('Arsenal FC', 'Coventry City FC', 'Arsenal', 'Coventry')
        assert sw is False and sc == 2.0

    def test_accept_requires_both_teams_and_margin(self):
        assert S.accept_match([(1.0, False, 1.0, 0.0, 1)]) is None          # only one team matches
        assert S.accept_match([(2.0, False, 1.0, 1.0, 1), (1.9, False, 1.0, 0.9, 2)]) is None   # ambiguous
        best = S.accept_match([(1.0, False, 0.5, 0.5, 2), (2.0, False, 1.0, 1.0, 1)])
        assert best[4] == 1
        assert S.accept_match([]) is None

    def test_dundee_is_not_dundee_united(self):
        # PM "Dundee United FC vs. Aberdeen FC" against FD "Falkirk v Dundee": one team only -> rejected
        sc, sw, a, b = S.pair_score('Dundee United FC', 'Aberdeen FC', 'Falkirk', 'Dundee')
        assert S.accept_match([(sc, sw, a, b, 0)]) is None


class TestTrading:
    def test_taker_cost_fee_formula(self):
        cost, ask = S.taker_cost(0.40, 0.01, rate=0.05)
        assert abs(ask - 0.41) < 1e-12
        assert abs(cost - (0.41 + 0.05 * 0.41 * 0.59)) < 1e-12

    def test_taker_cost_capped(self):
        cost, ask = S.taker_cost(0.995, 0.01, rate=0.05)
        assert ask == 0.99

    def test_maker_limit_and_fill(self):
        lim = S.maker_limit(0.40, 0.01)
        assert abs(lim - 0.39) < 1e-12
        assert not S.maker_filled(lim, [0.40, 0.395, 0.385])       # never a full tick through
        assert S.maker_filled(lim, [0.41, 0.38])                    # one tick through
        assert not S.maker_filled(lim, [])
        assert not S.maker_filled(lim, [None])

    def test_side_view_no_side(self):
        p, f, pay = S.side_view(0.3, 0.35, 1.0, 1)
        assert abs(p - 0.7) < 1e-12 and abs(f - 0.65) < 1e-12 and pay == 0.0
        assert S.side_view(0.3, 0.35, None, 1)[2] is None
        assert S.side_view(0.3, 0.35, 1.0, 0) == (0.3, 0.35, 1.0)

    def test_expected_return(self):
        assert abs(S.expected_return(0.5, 0.45) - (0.5 / 0.45 - 1)) < 1e-12
        assert S.expected_return(0.5, 0.0) is None

    def test_otype(self):
        fair = {'home': 0.5, 'draw': 0.27, 'away': 0.23}
        assert S.otype_of('home', fair) == 'fav'
        assert S.otype_of('away', fair) == 'dog'
        assert S.otype_of('draw', fair) == 'draw'

    def test_pick_signal(self):
        c = [{'ev': 0.02, 'otype': 'fav'}, {'ev': 0.07, 'otype': 'dog'}, {'ev': 0.04, 'otype': 'draw'},
             {'ev': None, 'otype': 'fav'}]
        assert S.pick_signal(c, 0.0, 'all')['ev'] == 0.07
        assert S.pick_signal(c, 0.03, 'fav') is None
        assert S.pick_signal(c, 0.03, 'draw')['ev'] == 0.04
        assert S.pick_signal(c, 0.08, 'all') is None

    def test_band10(self):
        assert S.band10(0.0) == 0 and S.band10(0.05) == 0 and S.band10(0.55) == 5 and S.band10(0.999) == 9
        assert S.band10(1.0) == 9

    def test_mid_at(self):
        s = [[1000, 0.4], [4600, 0.42], [8200, 0.45]]
        assert S.mid_at(s, 800) is None                 # market had not started
        assert S.mid_at(s, 4500) == 0.42                # a point stamped within 2 minutes after t counts
        assert S.mid_at(s, 4400) == 0.4
        assert S.mid_at([], 100) is None

    def test_peak_capital(self):
        tr = [{'ko': 10 * 3600, 'h': 2, 'r': 0.1}, {'ko': 11 * 3600, 'h': 2, 'r': -1.0},
              {'ko': 30 * 3600, 'h': 2, 'r': 0.0, 'filled': False}]
        assert S.peak_capital(tr, 100.0) == 200.0


class TestTennisNames:
    def test_td_player(self):
        assert S.td_player('Auger-Aliassime F.') == ({'auger', 'aliassime'}, 'f')
        assert S.td_player('De Minaur A.') == ({'de', 'minaur'}, 'a')

    def test_pm_player_match(self):
        assert S.pm_player_match('Frances Tiafoe', 'Tiafoe F.')
        assert S.pm_player_match('Félix Auger-Aliassime', 'Auger-Aliassime F.')
        assert S.pm_player_match('Alex de Minaur', 'De Minaur A.')
        assert not S.pm_player_match('Taylor Fritz', 'Tiafoe F.')

    def test_initial_disambiguates_siblings(self):
        assert S.pm_player_match('Karolina Pliskova', 'Pliskova K.')
        assert not S.pm_player_match('Jannik Sinner', 'Sinner X.')

    def test_td_date(self):
        assert S.td_date('46026') == dt.date(2026, 1, 4)
        assert S.td_date('04/01/2026') == dt.date(2026, 1, 4)
        assert S.td_date('x') is None


class TestPrints:
    YES, NO = 'y', 'n'

    def test_yes_prints_mirror(self):
        rows = [{'timestamp': 10, 'price': '0.40', 'size': '100', 'side': 'SELL', 'asset': 'y'},
                {'timestamp': 20, 'price': '0.62', 'size': '50', 'side': 'BUY', 'asset': 'n'},
                {'timestamp': 30, 'price': '0.37', 'size': '10', 'side': 'SELL', 'asset': 'n'}]
        p = S.yes_prints(rows, 'y')
        assert p[0] == (10, 0.40, 100.0, -1)                      # taker sold YES
        assert p[1][0] == 20 and abs(p[1][1] - 0.38) < 1e-12 and p[1][3] == -1   # buying NO at .62 sells YES at .38
        assert p[2][0] == 30 and abs(p[2][1] - 0.63) < 1e-12 and p[2][3] == 1    # selling NO at .37 buys YES at .63

    def test_print_fill_yes_side(self):
        pr = [(10, 0.40, 100.0, -1), (20, 0.39, 50.0, -1), (30, 0.38, 10.0, 1)]
        assert S.print_fill(pr, 0, 0.40, 0, 100) == (True, 0.40 * 50.0)   # only the print strictly below fills
        assert S.print_fill(pr, 0, 0.39, 0, 100)[0] is False                 # a print at the limit is not through
        assert S.print_fill(pr, 0, 0.40, 20, 100)[0] is False                # the print came before the order

    def test_print_fill_no_side(self):
        # resting NO bid at 0.60 fills when a taker buys YES above 0.40 (sells NO below 0.60)
        pr = [(10, 0.41, 20.0, 1), (20, 0.40, 30.0, 1), (30, 0.45, 5.0, -1)]
        hit, usd = S.print_fill(pr, 1, 0.60, 0, 100)
        assert hit and abs(usd - 0.60 * 20.0) < 1e-12
        assert S.print_fill([(20, 0.40, 30.0, 1)], 1, 0.60, 0, 100)[0] is False
