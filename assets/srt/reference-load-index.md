# SRT Reference Load Index

Load exactly one primary reference first. Add a second only when the task
genuinely crosses lanes. Do not bulk-load the full SRT library.

## Calibration And Legal Mechanics

| Task signal | Primary reference | Add only if needed |
| --- | --- | --- |
| Shared SRT lane contract, source-of-truth rules, stop/ask/second-look stance | `references/core-contract.md` | `references/response-structures.md` |
| New-deal calibration, required inputs, `L30`, or suspicious calibrated DM | `references/spreads-dm-calibration.md` | `references/legal-inputs.md` |
| Legal document, CDS confirmation, indenture, offering memo, or deal terms | `references/legal-inputs.md` | `references/model-input-cheatsheet.md` |
| SES, triggers, waterfall, split amortization, or legal pricing mechanics | `references/ses.md` | `references/srt-waterfall-and-triggers.md` |
| Quick cell list for calibration or quarterly update | `references/model-input-cheatsheet.md` | `references/model-cell-map.md` |
| New to this model's non-obvious cells or house conventions | `references/glossary.md` | `references/model-input-cheatsheet.md` |

## Registry Inputs

| Task signal | Primary reference | Add only if needed |
| --- | --- | --- |
| Registry/tape fields, RONA tie-out, source mapping, or obligor status | `references/registry-structure.md` | `adapters/canonical-registry-schema.md` |
| PD, LGD, recovery, severity, or missing credit inputs | `references/pd-lgd-severity.md` | `references/cln-aggregation.md` |
| CLN performance-curve aggregation, ratings buckets, or methodology path | `references/cln-aggregation.md` | `references/registry-structure.md` |
| Defaulted or non-liquidated borrower treatment | `references/defaulted-and-nonliquidated-borrowers.md` | `references/evidence.md` |

## Quarterly Model Update

| Task signal | Primary reference | Add only if needed |
| --- | --- | --- |
| Quarterly update, run classification, or step order | `references/process.md` | `references/stop-items.md` |
| Workbook inputs, named ranges, mapped-cell checks | `references/model-cell-map.md` | `references/model-input-cheatsheet.md` |
| Dates, valuation date, accrual, day count, or discount factors | `references/dates-rates-daycount.md` | `references/model-cell-map.md` |
| CDS / CDX / iTraxx spread change, Spread Analysis, or valuation-date DM | `references/benchmark-spread-pulling.md` | `references/spreads-dm-calibration.md` |

## Review And Common Questions

| Task signal | Primary reference | Add only if needed |
| --- | --- | --- |
| Mark moved: explain it with "vs. prior, because" | `templates/mark-attribution.md` | `references/spreads-dm-calibration.md` |
| Evidence log, exception log, output readiness, or client-facing gate | `references/evidence.md` | `references/report-lane.md` |
| Shaping any triggered answer; second-look or stop decision | `references/response-structures.md` | `references/stop-items.md` |
| Recurring tricky confusion or theory question | `references/common-confusions.md` | the lane-specific reference above |
| Quick cell list for a simple analyst question | `references/model-input-cheatsheet.md` | `references/model-cell-map.md` |

## Optional Conceptual References

Load only when the user asks for concepts/theory or when a deal-specific issue
needs explanation. These references do not override deal documents, model
mapping, current source data, or a colleague's review.

| Topic | Reference |
| --- | --- |
| SRT/CLN structure and reference-portfolio concepts | `references/srt-theory-primer.md` |
| PD/LGD/recovery theory and RONA weighting | `references/credit-risk-parameter-theory.md` |
| Waterfall, sequential triggers, attach/detach, split amortization | `references/srt-waterfall-and-triggers.md` |
| Multiplier and spread-change theory | `references/benchmark-spread-pulling.md` |
| Default correlation & the Gaussian-copula correlation exhibit (report-only) | `references/srt-copula-theory.md` |
