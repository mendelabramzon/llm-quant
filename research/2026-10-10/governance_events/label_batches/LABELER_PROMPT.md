# Prompt given to every labeling pass (verbatim; only BATCH changes)

You are one of several parallel labelers in a research study. Your only job is to label every DAO governance proposal
packet in ONE batch against a fixed rubric. Work directly; do not delegate.

1. Read the rubric in full: `/Users/iv/dev/llm-quant/research/2026-10-10/governance_events/criteria.md`
2. Read your whole batch: `/Users/iv/dev/llm-quant/research/2026-10-10/governance_events/label_batches/{BATCH_MD}`.
   Each packet starts with a line `[k] id=... token=... space=... date=...`, then TITLE, CHOICES and TEXT (the first
   1,500 characters of the proposal). Page through the file with the Read tool's offset/limit until you have read every
   packet; do not skip any.
3. For every packet decide, using only the rubric and the packet:
   - `label`: VALUE_UP, VALUE_DOWN or NEUTRAL
   - `surprise`: true or false
   - `confidence`: a number from 0 to 1
   - `binding`: signal, binding or unknown
   - `reason`: one line, at most 200 characters, naming the concrete economic change (for example "buys back UNI with
     protocol fees", "50M ARB incentive program", "gauge addition within fixed emissions").
4. Write all labels to `/Users/iv/dev/llm-quant/research/2026-10-10/governance_events/label_batches/{OUT_FILE}`: one JSON
   object per line, `{"id": "...", "label": "...", "surprise": true, "confidence": 0.8, "binding": "unknown",
   "reason": "..."}`, in packet order, every id exactly once (copy ids exactly as printed). Write the file with the
   Write tool (or in a few appends if it is long).
5. Validate: `cd /Users/iv/dev/llm-quant && python3 scripts/governance_events.py label-check --out
   research/2026-10-10/governance_events --batch {BATCH_ID}` must print `OK ...`. Fix and re-run until it does.

Rules:
- Use ONLY the rubric and the packets. Do not open any other file in the repository (not candidates.jsonl,
  labels.jsonl, manifest.json, raw/, analysis or tables files, other batches or their outputs). Do not search the web.
  Do not look up prices, news, forum posts or vote outcomes.
- Label by what the proposal would do if implemented, not by whether it passed or how the vote went.
- Most proposals are NEUTRAL; that is expected. Apply the rubric's materiality rules (small grants and routine
  operations are NEUTRAL).
- The label concerns the space's own token (shown as `token=`), not other tokens the proposal mentions.
- Be consistent: the same kind of proposal gets the same label wherever it appears.

Final message: the number of packets labeled, the count per label, and up to five packets you found hardest (id and why).
