# Labeling criteria — governance_events

Written 2026-10-10, before any proposal was labeled and before any price was downloaded or computed. These criteria
do not change after a price is seen; `label-freeze` records this file's sha256 next to the labels' sha256 in
`manifest.json`, and a later edit is visible as a hash mismatch.

## What the labeler sees

One packet per candidate Snapshot proposal: the token, the Snapshot space, the UTC date it was published, the title,
the voting choices, and the first 1,500 characters of the body. Nothing else — no price, no vote outcome or tally, no
keyword-screen result, no flag saying whether the proposal is a keyword hit or a random control. The labeler must not
look anything up (no news, no prices, no forum) and labels only from the packet.

## The question

> If this proposal were implemented as written, would it directly and materially change the cash flow reaching holders
> of THIS token (or its staked / vote-escrowed form), or this token's supply or supply growth, compared with the status
> quo on the proposal's date?

Label by what the proposal would do if implemented, not by whether it is likely to pass. The label is about the token
of the space (UNI for uniswapgovernance.eth, CRV for curve.eth, ...), not about other tokens the proposal mentions.

## Labels

**VALUE_UP** — implemented, it directly raises cash flow to holders/stakers or cuts supply or supply growth:

- turns on (or raises) a fee switch / protocol fee whose proceeds go to token holders or stakers, or are used to buy
  the token;
- buys back the token (open market, from revenue or treasury non-token assets), or burns tokens (including burning
  treasury-held or unallocated tokens);
- introduces or raises revenue / fee / profit sharing to holders or stakers (paid in ETH, stablecoins, or the token
  bought with revenue);
- cuts emissions or inflation, cancels or shrinks an unminted / unvested allocation, adds a supply cap, extends a lock;
- pays staking rewards out of protocol revenue rather than new emissions;
- distributes non-token treasury assets (stablecoins, ETH) to holders;
- cancels or claws back a previously approved token-paid program (the tokens are no longer emitted).

**VALUE_DOWN** — implemented, it dilutes holders or adds sell pressure on the token:

- new or raised emissions / inflation, minting new tokens, a new reward stream paid from newly issued tokens;
- sells treasury tokens (OTC, market sale, sale to a fund or market maker, a "diversification" that converts the token
  into stablecoins / ETH / RWAs, a token sale round);
- a large grant, incentive program, liquidity-mining program or ecosystem fund paid in the token. *Material* means any
  of: at least about 1% of circulating supply (use general knowledge of the token's supply), at least $5M, or a
  multi-season / multi-year program. A small grant, a bounty, a working-group budget, or a program without a stated size
  that reads as small is NEUTRAL;
- accelerates unlocks / vesting, releases locked or escrowed tokens early, removes a lock;
- redirects fees or revenue away from token holders (to the treasury, to another constituency) or turns a fee switch
  off.

**NEUTRAL** — everything else, including: risk and protocol parameters, asset listings, chain deployments, gauge
additions and gauge-weight votes that reallocate a fixed emission budget, farm / pool additions within an existing
budget, elections and council seats, delegate programs, partnerships, legal / branding / process changes, operating
budgets and grants paid in stablecoins or ETH, treasury swaps that do not sell the token, small token grants, and
signalling text with no concrete economic change.

**Mixed proposals.** Weigh the net effect on holders using the magnitudes stated (for example a fee switch funded
partly by new emissions). If the net direction is genuinely unclear, use NEUTRAL with low confidence and say why.

**Option menus.** When the choices are alternative sizes or designs ("burn 10% / 20% / do nothing"), label by the
direction shared by the non-status-quo options; if the options point in opposite directions, NEUTRAL.

**Materiality for VALUE_UP.** Ongoing mechanisms (a fee switch, a revenue share, a recurring buyback, an emission cut)
are material by nature. A one-off buyback or burn is material if it is at least about $1M or about 0.5% of supply, or
is presented as a significant tokenomics change; a token-dust burn is NEUTRAL.

## Surprise flag

- `surprise: true` — the packet reads as the first public appearance on Snapshot of this economic change: a new idea,
  a first temperature check, no reference to an earlier vote on the same change.
- `surprise: false` — a continuation: the final vote after a temperature check, a re-vote, a renewal / extension /
  next season or phase of a known program, the implementation of an already-approved plan, a routine or recurring
  action (the next monthly buyback execution, the next emissions epoch).

Batches are in token and time order so an earlier packet of the same plan is visible. Set the flag for NEUTRAL labels
by the same rule (it is recorded but not used).

## Binding

`binding`: `signal` when the packet is a temperature check, RFC / ARFC, poll or sentiment vote, or says an on-chain
vote follows; `binding` when the text says this vote is final or executes directly (multisig, oSnap, council
execution, or a DAO that uses Snapshot as its final vote); otherwise `unknown`.

## Confidence

A number in [0, 1]: the probability that a careful second reader with these criteria would give the same label.
Use 0.8 or more when the packet states the economic change and its direction explicitly; 0.5–0.8 when it is implied or
the size is uncertain; below 0.5 when the first 1,500 characters do not make the economics clear.

## Output

One JSON object per packet, one per line, every packet exactly once:

```
{"id": "<proposal id>", "label": "VALUE_UP|VALUE_DOWN|NEUTRAL", "surprise": true|false, "confidence": 0.0-1.0,
 "binding": "signal|binding|unknown", "reason": "<one line, at most 200 characters>"}
```

## Procedure

1. The keyword screen and a random control sample of non-matching proposals define the candidates
   (`governance_events.py screen`); `label-export` writes the packets in batches and a shuffled 10% spot-check sample.
2. Every batch is labeled with this file and nothing else. Batches are labeled in separate passes; no pass sees prices.
3. `label-freeze` validates that every candidate has exactly one valid label, writes `labels.jsonl`, and stamps the
   time, the labels' sha256 and this file's sha256 into `manifest.json`. The train/test cutoff is fixed at the same
   moment from label dates only.
4. The spot-check sample is re-labeled blind by a separate pass that sees neither the first labels nor any price;
   `label-agree` reports agreement, Cohen's kappa and every disagreement.
5. Only then are price paths computed (`analyze` refuses to run if `labels.jsonl` no longer matches its frozen hash).
