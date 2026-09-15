---
name: srt-review-package
description: Use when SRT/CLN work involves evidence, mark attribution, exception logs, unexplained price moves, output readiness, review language, shadow measurement, or second-look calls for default severity, benchmark choice, or DM embedding.
---

# SRT Review Package

Make the valuation reviewable; do not approve the mark.

Load `core-contract.md`, then the load index.

Evidence: record workflow, asset class, source, action, output/result, status,
exception, owner/reviewer, and date/time when relevant. Use
`evidence-log.csv` and `exception-log.csv`.

Attribution: every mark needs a "vs. prior, because" bridge using
`mark-attribution.md`. Decompose rates, spread/DM, paydown/amortization, credit,
date/accrual, methodology, and default treatment.

Second look: Do not escalate a fixed legal term, normal mechanic, or registry
gap. Optional second look - framed as a second reviewer, never a specific person
- only for defaulted/non-liquidated severity with no governing contract,
benchmark selection, or how much spread change to embed in DM. Give factors and
recommendation first.

Shadow measurement: `../../scripts/srt-review-package/shadow_run.py` compares
inputs to a prior/human mark without writing the model.

References: `evidence.md`, `stop-items.md`, `response-structures.md`,
`report-lane.md`.
