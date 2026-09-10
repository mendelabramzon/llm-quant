"""A temporary same-block squeeze must not turn into hours of illiquidity."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from live_scan import State
from detectors.liquidity_blackout import scan


class RateOrderTests(unittest.TestCase):
    def test_log_order_and_final_block_updates_survive_summary(self):
        points = [(n,n*12,.4,.5,10) for n in range(1,83)] + [(n,n*12,.03,.04,20) for n in range(1,83)]
        state=SimpleNamespace(rates={('Aave v3','token'):points},p=SimpleNamespace(token=lambda _:('TEST',18,'USD')))
        row=State.rates_summary(state)[0]
        self.assertEqual(row['borrow_first'],.5)
        self.assertEqual(row['borrow_last'],.04)
        self.assertEqual(len(row['block_end_series']),82)
        self.assertTrue(all(p[2]==.04 for p in row['block_end_series']))
        with tempfile.TemporaryDirectory() as d:
            Path(d,'head_state.json').write_text(json.dumps({'rate_curves':{'Aave v3 TEST':{
                'base':.01,'optimal':.9,'slope1':.04,'slope2':.5}},
                'lending':{'Aave v3':{'token':{'supplied_usd':8e6}}}}))
            ctx=SimpleNamespace(out=Path(d),analysis={'lending_rates':[row]},
                                blocks=[{'n':n,'ts':n*12} for n in range(1,84)])
            self.assertEqual(scan(ctx),[])
            row['block_end_series']=[[n,n*.001,.5] for n in range(1,83)]
            self.assertEqual(len(scan(ctx)),1)
            del row['block_end_series']
            self.assertEqual(scan(ctx),[]) # A legacy downsample cannot prove duration.
