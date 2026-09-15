---
name: srt-quarterly-update
description: Use when SRT/CLN work needs the router for Srt dcf.xlsm: calibration, quarterly update, registry/RONA, PD/LGD, H10/H11, spreads, SES/triggers, evidence, review, conceptual questions, or copula. Not CRE/CLO/consumer-pool/debt-stack/generic models.
---

# SRT Quarterly Update Router

Classify the request, then load only the lane/reference needed. `Srt dcf.xlsm`
remains the calculation source of truth.

If ambiguous, ask: `Is this a new-deal calibration or a quarterly update?`

Load `../../assets/srt/references/core-contract.md`, then the load index. Do
not bulk-load references.

| Goal | Lane |
|---|---|
| New-deal inputs, `L30`, par solve, calibrated DM | `srt-calibration` |
| Legal terms, SES, triggers, amortization, settlement | `srt-legal-deal-mechanics` |
| Registry/tape, RONA, ratings, PD/LGD/recovery, CLN aggregation | `srt-registry-inputs` |
| Quarterly cells, H10/H11, rates/DFs, spread change, checks, mark movement | `srt-quarterly-model-update` |
| Evidence, attribution, exceptions, shadow run, readiness, second look | `srt-review-package` |
| Conceptual "why" questions | `srt-difficulties` |
| Correlation / Gaussian copula; report-only | `srt-copula` |

If one lane fits, answer there. If multiple fit, answer the core question and
load only the supplement. Use `response-structures.md` for stance.
