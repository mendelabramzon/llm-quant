"""cow_fill_check: the GPv2 Trade decoder reads the ABI layout the settlement contract emits."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cow_fill_check as C   # noqa: E402


def _w(x):
    return format(x, '064x')


def test_decode_trade_reads_amounts_tokens_and_uid():
    sell, buy = int(C.WETH, 16), int('0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee', 16)
    uid = 'ab' * 56                                       # 32-byte digest + 20-byte owner + 4-byte validTo
    data = '0x' + _w(sell) + _w(buy) + _w(10 ** 18) + _w(97 * 10 ** 16) + _w(0) + _w(0xc0) + _w(56) + uid + '0' * 16
    log = {'blockNumber': hex(25_000_000), 'transactionHash': '0x01', 'data': data,
           'topics': [C.TRADE_TOPIC, '0x' + '0' * 24 + '11' * 20]}
    t = C.decode_trade(log)
    assert t['sell_token'] == C.WETH
    assert t['buy_token'] == '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee'
    assert (t['sell_amount'], t['buy_amount'], t['fee_amount']) == (10 ** 18, 97 * 10 ** 16, 0)
    assert t['uid'] == '0x' + uid and t['owner'] == '0x' + '11' * 20 and t['block'] == 25_000_000
