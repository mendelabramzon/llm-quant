#!/usr/bin/env python3
"""Pure-python decoders for Solana `json`-encoded transactions: base58, account-key resolution (static keys + address-table
loaded keys), instruction iteration with call depth, and decoders for the System, SPL Token / Token-2022, Compute Budget
and Anchor-discriminated instructions this research needs (CCTP depositForBurn). Validated against the RPC's own
`jsonParsed` output for the same block by `python scripts/solana_decode.py validate <json.gz> <jsonParsed.gz>`.
"""
import gzip
import hashlib
import json
import struct
import sys

ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
_IDX = {c: i for i, c in enumerate(ALPHABET)}

SYSTEM = '11111111111111111111111111111111'
TOKEN = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
TOKEN_2022 = 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'
ATA = 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'
COMPUTE_BUDGET = 'ComputeBudget111111111111111111111111111111'
VOTE = 'Vote111111111111111111111111111111111111111'
MEMO = 'MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr'
MEMO_V1 = 'Memo1UhkJRfHyvLMcVucJwxXeuD728EqVDDwQDxFMNo'
STAKE = 'Stake11111111111111111111111111111111111111'
CCTP_MESSAGE_TRANSMITTER = 'CCTPmbSD7gX1bxKPAmg77w8oFzNFpaQiQUWD43TKaecd'
CCTP_TOKEN_MESSENGER = 'CCTPiPYPc6AsJuwueEnWgSgucamXDZwBd53dQ11YiKX3'
CCTP_V2_MESSAGE_TRANSMITTER = 'CCTPV2vPZJS2u2BBsUoscuikbYjnpFmbFsvVuJdgUMQe'
CCTP_V2_TOKEN_MESSENGER = 'CCTPV2Sm4AdWt5296sk4P66VBZ7bEhcARwFaaS9YPbeC'
CCTP_DOMAINS = {0: 'Ethereum', 1: 'Avalanche', 2: 'OP Mainnet', 3: 'Arbitrum', 4: 'Noble', 5: 'Solana', 6: 'Base', 7: 'Polygon', 8: 'Sui', 9: 'Aptos',
                10: 'Unichain', 11: 'Linea', 12: 'Codex', 13: 'Sonic', 14: 'World Chain', 16: 'Sei', 19: 'HyperEVM', 21: 'Ink', 22: 'Plume', 24: 'Monad'}


def b58decode(s):
    n = 0
    for c in s:
        n = n * 58 + _IDX[c]
    body = n.to_bytes((n.bit_length() + 7) // 8, 'big') if n else b''
    pad = len(s) - len(s.lstrip('1'))
    return b'\x00' * pad + body


def b58encode(b):
    n = int.from_bytes(b, 'big')
    out = ''
    while n:
        n, r = divmod(n, 58)
        out = ALPHABET[r] + out
    pad = len(b) - len(b.lstrip(b'\x00'))
    return '1' * pad + out


def anchor_disc(name):
    return hashlib.sha256(('global:' + name).encode()).digest()[:8]


def tx_keys(tx):
    """Full ordered key list: static account keys, then address-table loaded writable, then loaded readonly."""
    msg = tx['transaction']['message']
    keys = list(msg['accountKeys'])
    la = tx['meta'].get('loadedAddresses') or {}
    keys += la.get('writable') or []
    keys += la.get('readonly') or []
    return keys


def iter_instructions(tx, keys=None):
    """Yield dicts {program, accounts (pubkeys), data (bytes), depth, outer} for top-level and inner instructions in execution order."""
    keys = keys or tx_keys(tx)
    msg = tx['transaction']['message']
    inner = {}
    for group in tx['meta'].get('innerInstructions') or []:
        inner[group['index']] = group['instructions']
    for i, ix in enumerate(msg['instructions']):
        yield _ix(ix, keys, 1, i)
        for jx in inner.get(i, []):
            yield _ix(jx, keys, jx.get('stackHeight') or 2, i)


def _ix(ix, keys, depth, outer):
    try:
        prog = keys[ix['programIdIndex']]
        accts = [keys[a] for a in ix['accounts']]
    except IndexError:
        prog, accts = '?', []
    try:
        data = b58decode(ix['data']) if ix.get('data') else b''
    except KeyError:
        data = b''
    return {'program': prog, 'accounts': accts, 'data': data, 'depth': depth, 'outer': outer}


def decode(ix):
    """Return a dict describing a known instruction, or None."""
    p, d, a = ix['program'], ix['data'], ix['accounts']
    if p == SYSTEM and len(d) >= 4:
        k = struct.unpack_from('<I', d, 0)[0]
        if k == 2 and len(d) >= 12:
            return {'kind': 'sys_transfer', 'lamports': struct.unpack_from('<Q', d, 4)[0], 'from': a[0] if a else None, 'to': a[1] if len(a) > 1 else None}
        if k == 0 and len(d) >= 52:
            lam, space = struct.unpack_from('<QQ', d, 4)
            return {'kind': 'sys_create_account', 'lamports': lam, 'space': space, 'owner': b58encode(d[20:52]), 'from': a[0] if a else None, 'new': a[1] if len(a) > 1 else None}
        if k == 3 and len(d) >= 12:
            return {'kind': 'sys_create_account_with_seed', 'from': a[0] if a else None, 'new': a[1] if len(a) > 1 else None}
        if k == 11 and len(d) >= 12:
            return {'kind': 'sys_transfer_with_seed', 'lamports': struct.unpack_from('<Q', d, 4)[0], 'from': a[0] if a else None, 'to': a[2] if len(a) > 2 else None}
        names = {1: 'sys_assign', 4: 'sys_advance_nonce', 5: 'sys_withdraw_nonce', 6: 'sys_initialize_nonce', 7: 'sys_authorize_nonce', 8: 'sys_allocate', 9: 'sys_allocate_with_seed', 10: 'sys_assign_with_seed', 12: 'sys_upgrade_nonce'}
        return {'kind': names.get(k, 'sys_%d' % k)}
    if p in (TOKEN, TOKEN_2022) and d:
        k = d[0]
        tp = 'token2022' if p == TOKEN_2022 else 'token'
        if k == 3 and len(d) >= 9:
            return {'kind': 'transfer', 'program': tp, 'amount': struct.unpack_from('<Q', d, 1)[0], 'source': a[0] if a else None, 'dest': a[1] if len(a) > 1 else None, 'authority': a[2] if len(a) > 2 else None}
        if k == 12 and len(d) >= 10:
            return {'kind': 'transferChecked', 'program': tp, 'amount': struct.unpack_from('<Q', d, 1)[0], 'decimals': d[9], 'source': a[0] if a else None, 'mint': a[1] if len(a) > 1 else None, 'dest': a[2] if len(a) > 2 else None, 'authority': a[3] if len(a) > 3 else None}
        if k == 7 and len(d) >= 9:
            return {'kind': 'mintTo', 'program': tp, 'amount': struct.unpack_from('<Q', d, 1)[0], 'mint': a[0] if a else None, 'dest': a[1] if len(a) > 1 else None, 'authority': a[2] if len(a) > 2 else None}
        if k == 14 and len(d) >= 10:
            return {'kind': 'mintToChecked', 'program': tp, 'amount': struct.unpack_from('<Q', d, 1)[0], 'decimals': d[9], 'mint': a[0] if a else None, 'dest': a[1] if len(a) > 1 else None, 'authority': a[2] if len(a) > 2 else None}
        if k == 8 and len(d) >= 9:
            return {'kind': 'burn', 'program': tp, 'amount': struct.unpack_from('<Q', d, 1)[0], 'account': a[0] if a else None, 'mint': a[1] if len(a) > 1 else None, 'authority': a[2] if len(a) > 2 else None}
        if k == 15 and len(d) >= 10:
            return {'kind': 'burnChecked', 'program': tp, 'amount': struct.unpack_from('<Q', d, 1)[0], 'decimals': d[9], 'account': a[0] if a else None, 'mint': a[1] if len(a) > 1 else None, 'authority': a[2] if len(a) > 2 else None}
        names = {0: 'initializeMint', 1: 'initializeAccount', 2: 'initializeMultisig', 4: 'approve', 5: 'revoke', 6: 'setAuthority', 9: 'closeAccount', 10: 'freezeAccount', 11: 'thawAccount',
                 13: 'approveChecked', 16: 'initializeAccount2', 17: 'syncNative', 18: 'initializeAccount3', 19: 'initializeMultisig2', 20: 'initializeMint2', 21: 'getAccountDataSize',
                 22: 'initializeImmutableOwner', 23: 'amountToUiAmount', 24: 'uiAmountToAmount', 25: 'initializeMintCloseAuthority', 26: 'transferFeeExtension', 27: 'confidentialTransferExtension',
                 28: 'defaultAccountStateExtension', 29: 'reallocate', 30: 'memoTransferExtension', 31: 'createNativeMint', 32: 'initializeNonTransferableMint', 33: 'interestBearingMintExtension',
                 34: 'cpiGuardExtension', 35: 'initializePermanentDelegate', 36: 'transferHookExtension', 37: 'confidentialTransferFeeExtension', 38: 'withdrawExcessLamports', 39: 'metadataPointerExtension',
                 40: 'groupPointerExtension', 41: 'groupMemberPointerExtension', 43: 'scaledUiAmountExtension', 44: 'pausableExtension'}
        return {'kind': names.get(k, '%s_%d' % (tp, k)), 'program': tp}
    if p == COMPUTE_BUDGET and d:
        k = d[0]
        if k == 2 and len(d) >= 5:
            return {'kind': 'cu_limit', 'units': struct.unpack_from('<I', d, 1)[0]}
        if k == 3 and len(d) >= 9:
            return {'kind': 'cu_price', 'micro_lamports': struct.unpack_from('<Q', d, 1)[0]}
        if k == 1 and len(d) >= 5:
            return {'kind': 'heap_frame', 'bytes': struct.unpack_from('<I', d, 1)[0]}
        if k == 4 and len(d) >= 5:
            return {'kind': 'loaded_data_limit', 'bytes': struct.unpack_from('<I', d, 1)[0]}
        return {'kind': 'compute_budget_%d' % k}
    if p in (CCTP_TOKEN_MESSENGER, CCTP_V2_TOKEN_MESSENGER) and len(d) >= 8:
        disc = d[:8]
        if disc == anchor_disc('deposit_for_burn') and len(d) >= 52:
            amount, domain = struct.unpack_from('<QI', d, 8)
            return {'kind': 'cctp_deposit_for_burn', 'version': 2 if p == CCTP_V2_TOKEN_MESSENGER else 1, 'amount': amount, 'destination_domain': domain,
                    'destination': CCTP_DOMAINS.get(domain, 'domain %d' % domain), 'mint_recipient': '0x' + d[20:52].hex()}
        if disc == anchor_disc('deposit_for_burn_with_caller') and len(d) >= 84:
            amount, domain = struct.unpack_from('<QI', d, 8)
            return {'kind': 'cctp_deposit_for_burn', 'version': 1, 'amount': amount, 'destination_domain': domain,
                    'destination': CCTP_DOMAINS.get(domain, 'domain %d' % domain), 'mint_recipient': '0x' + d[20:52].hex(), 'with_caller': True}
        if disc == anchor_disc('handle_receive_message') or disc == anchor_disc('handle_receive_finalized_message') or disc == anchor_disc('handle_receive_unfinalized_message'):
            return {'kind': 'cctp_handle_receive', 'version': 2 if p == CCTP_V2_TOKEN_MESSENGER else 1}
        return {'kind': 'cctp_messenger_other'}
    if p in (CCTP_MESSAGE_TRANSMITTER, CCTP_V2_MESSAGE_TRANSMITTER) and len(d) >= 8:
        if d[:8] == anchor_disc('receive_message'):
            # args: message: Vec<u8>, attestation: Vec<u8>; message header: version u32 BE, source domain u32 BE, dest domain u32 BE
            ln = struct.unpack_from('<I', d, 8)[0]
            msg = d[12:12 + ln]
            src = struct.unpack_from('>I', msg, 4)[0] if len(msg) >= 12 else None
            return {'kind': 'cctp_receive_message', 'version': 2 if p == CCTP_V2_MESSAGE_TRANSMITTER else 1, 'source_domain': src, 'source': CCTP_DOMAINS.get(src, 'domain %s' % src)}
        return {'kind': 'cctp_transmitter_other'}
    return None


def token_deltas(tx, keys=None):
    """Net token change per token account: {account_pubkey: {'mint','owner','delta_raw','decimals','pre','post'}} from pre/post balances."""
    keys = keys or tx_keys(tx)
    out = {}
    for side, sign in (('preTokenBalances', 'pre'), ('postTokenBalances', 'post')):
        for a in tx['meta'].get(side) or []:
            acct = keys[a['accountIndex']] if a['accountIndex'] < len(keys) else '?%d' % a['accountIndex']
            amt = a['amount'] if 'amount' in a else a['uiTokenAmount']['amount']
            dec = a['decimals'] if 'decimals' in a else a['uiTokenAmount']['decimals']
            e = out.setdefault(acct, {'mint': a['mint'], 'owner': a.get('owner'), 'programId': a.get('programId'), 'decimals': dec, 'pre': 0, 'post': 0})
            e[sign] = int(amt)
            if a.get('owner'):
                e['owner'] = a['owner']
    for e in out.values():
        e['delta_raw'] = e['post'] - e['pre']
    return out


def sol_deltas(tx, keys=None):
    keys = keys or tx_keys(tx)
    pre, post = tx['meta']['preBalances'], tx['meta']['postBalances']
    return {keys[i]: post[i] - pre[i] for i in range(min(len(keys), len(pre), len(post))) if post[i] != pre[i]}


def validate(json_path, parsed_path):
    """Compare this module's decoding of a `json` block with the RPC's `jsonParsed` decoding of the same block."""
    with gzip.open(json_path, 'rt') as f:
        bj = json.load(f)
    with gzip.open(parsed_path, 'rt') as f:
        bp = json.load(f)
    assert bj['blockhash'] == bp['blockhash'], 'different blocks'
    mism = 0
    checked = 0
    kinds = {}
    for tj, tp in zip(bj['transactions'], bp['transactions']):
        if VOTE in tj['transaction']['message']['accountKeys']:
            continue
        keys = tx_keys(tj)
        pkeys = [a['pubkey'] for a in tp['transaction']['message']['accountKeys']]
        la = tp['meta'].get('loadedAddresses') or {}
        pkeys += (la.get('writable') or []) + (la.get('readonly') or [])
        assert keys == pkeys, 'key order differs'
        mine = [decode(ix) for ix in iter_instructions(tj, keys)]
        # parsed side, same order
        theirs = []
        inner = {g['index']: g['instructions'] for g in tp['meta'].get('innerInstructions') or []}
        for i, ix in enumerate(tp['transaction']['message']['instructions']):
            theirs.append(ix)
            theirs.extend(inner.get(i, []))
        assert len(mine) == len(theirs), 'instruction count differs %d vs %d' % (len(mine), len(theirs))
        for m, t in zip(mine, theirs):
            pr = t.get('parsed')
            if not isinstance(pr, dict):
                continue
            typ, info = pr.get('type'), pr.get('info', {})
            if t.get('program') == 'spl-token' and typ in ('transfer', 'transferChecked', 'mintTo', 'mintToChecked', 'burn', 'burnChecked'):
                checked += 1
                amt = int(info.get('amount') or info.get('tokenAmount', {}).get('amount'))
                ok = m and m['kind'] == typ and m['amount'] == amt and (m.get('source') or m.get('mint') or m.get('account')) == (info.get('source') or info.get('mint') or info.get('account'))
                kinds[typ] = kinds.get(typ, 0) + 1
            elif t.get('program') == 'system' and typ == 'transfer':
                checked += 1
                ok = m and m['kind'] == 'sys_transfer' and m['lamports'] == int(info['lamports']) and m['from'] == info['source'] and m['to'] == info['destination']
                kinds[typ] = kinds.get(typ, 0) + 1
            elif t.get('program') == 'system' and typ == 'createAccount':
                checked += 1
                ok = m and m['kind'] == 'sys_create_account' and m['lamports'] == int(info['lamports']) and m['owner'] == info['owner']
                kinds[typ] = kinds.get(typ, 0) + 1
            else:
                continue
            if not ok:
                mism += 1
                if mism <= 5:
                    print('MISMATCH', json.dumps(m)[:200], '|', json.dumps(pr)[:300])
    print('checked %d parsed instructions, %d mismatches; kinds %s' % (checked, mism, kinds))
    return mism == 0


if __name__ == '__main__':
    if sys.argv[1] == 'validate':
        sys.exit(0 if validate(sys.argv[2], sys.argv[3]) else 1)
