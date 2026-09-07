#!/usr/bin/env python3
"""The detector registry: every mechanism the loop has discovered, re-checked on every window.

Why. Each session so far produced one-off code — the just-in-time liquidity test, the midnight-routine query, the
address-poisoning matcher, the gas-hog attribution, the CoreVault fork hunt. When the session ended, the code stopped
running, so the next window rediscovered nothing and the system forgot. Meanwhile the *type registry* grew to ninety
entries precisely because it was a registry: adding to it was cheap and running it was automatic.

A detector is that same bargain for mechanisms. Each module exposes:

    NAME, DESCRIPTION, SEVERITY
    def scan(ctx) -> list[Hit]

`ctx` is a `Context` holding the window, its analysis, the address book and the price basis, built once and shared, so
adding a detector costs a function rather than another pass over 200 GB of blocks. A `Hit` carries evidence a reader can
chase — block, transaction, address — and, when the finding is an opportunity rather than an observation, an
`economics` verdict from `economics.py` so a live mechanism that nets $7 a run is labelled dust in the same breath.

The registry is deliberately unopinionated about what a detector looks for. The rule is only that it runs every window
and reports in one shape, which is what makes a past discovery something the system keeps rather than something it did.

    uv run --with pycryptodome python scripts/detectors/run.py --out research/2026-09-07/live_midday
"""
import dataclasses
import importlib
import json
import pkgutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SEVERITIES = ['info', 'notable', 'high']


@dataclasses.dataclass
class Hit:
    """One finding. `evidence` must let a reader reach the chain; `economics` prices it when it is actionable."""
    detector: str
    title: str
    severity: str = 'notable'
    evidence: Dict[str, Any] = dataclasses.field(default_factory=dict)
    economics: Optional[Dict[str, Any]] = None
    usd: Optional[float] = None

    def as_dict(self):
        return dataclasses.asdict(self)


class Context:
    """Everything a detector needs, loaded once and shared across the whole set."""

    def __init__(self, out, min_usd=1e4):
        from window_raw import Window
        import live_scan
        self.out = Path(out)
        self.window = Window(out)
        self.analysis = self.window.analysis
        self.prices = self.window.prices
        self.book = live_scan.load_address_book()
        self.min_usd = min_usd
        self._blocks = None
        self._transfers = None

    @property
    def blocks(self):
        """Per-block base fee and gas, materialised once."""
        if self._blocks is None:
            self._blocks = self.window.block_stats()
        return self._blocks

    @property
    def transfers(self):
        """Priced value legs at or above `min_usd`, materialised once and reused by every detector."""
        if self._transfers is None:
            self._transfers = list(self.window.transfers(min_usd=self.min_usd))
        return self._transfers

    def label(self, a):
        b = self.book.get(a)
        return b['label'] if b else None

    def kind(self, a):
        b = self.book.get(a)
        return b.get('kind') if b else None


def registry():
    """Every detector module in this package, in a stable order."""
    mods = []
    here = Path(__file__).resolve().parent
    for m in sorted(pkgutil.iter_modules([str(here)]), key=lambda x: x.name):
        if m.name.startswith('_') or m.name == 'run':
            continue
        mod = importlib.import_module('detectors.' + m.name)
        if hasattr(mod, 'scan'):
            mods.append(mod)
    return mods


def run_all(ctx, only=None):
    """Run every detector against one window and return hits plus a per-detector timing/error record."""
    hits, meta = [], []
    for mod in registry():
        name = getattr(mod, 'NAME', mod.__name__.split('.')[-1])
        if only and name not in only:
            continue
        t0 = time.monotonic()
        try:
            found = list(mod.scan(ctx) or [])
            err = None
        except Exception as e:
            found, err = [], '%s: %s' % (type(e).__name__, str(e)[:160])
        hits.extend(found)
        meta.append({'detector': name, 'hits': len(found), 'seconds': round(time.monotonic() - t0, 2),
                     'error': err, 'description': getattr(mod, 'DESCRIPTION', '')})
    order = {s: i for i, s in enumerate(reversed(SEVERITIES))}
    hits.sort(key=lambda h: (order.get(h.severity, 9), -(h.usd or 0)))
    return hits, meta
