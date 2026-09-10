import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from detectors import token_fan_in as f


class FanInTests(unittest.TestCase):
    def test_settlement_without_usd_price_and_distinct_sender_gate(self):
        token,recipient='0x'+'a'*40,'0x'+'b'*40
        def log(sender,to=recipient,amount=5):
            return {'address':token,'transactionHash':hex(sender),'topics':[f.TRANSFER,
                '0x'+hex(sender)[2:].rjust(64,'0'),'0x'+to[2:].rjust(64,'0')],
                'data':'0x'+hex(amount)[2:].rjust(64,'0')}
        with tempfile.TemporaryDirectory() as d,patch.object(f,'MIN_SENDERS',3):
            def scan(logs):
                w=SimpleNamespace(blocks=lambda:iter([({'number':'0x1','timestamp':'0x384'},logs)]),
                                  symbol=lambda t:None,tokens={})
                return f.scan(SimpleNamespace(out=Path(d),window=w,label=lambda a:None))
            hits=scan([log(1),log(2),log(3),log(0),log(4,amount=0)])
            self.assertEqual(len(hits),1)
            self.assertEqual(hits[0].evidence['total_raw'],'15')
            self.assertIsNone(hits[0].evidence['total_units'])
            self.assertEqual(scan([log(1),log(1),log(1)]),[])
            self.assertEqual(scan([log(i,'0x'+hex(i+100)[2:].rjust(40,'0')) for i in range(1,9)]),[])


if __name__=='__main__':
    unittest.main()
