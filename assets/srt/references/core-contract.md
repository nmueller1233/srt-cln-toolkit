# SRT Core Contract

Use this shared contract before any SRT / CLN lane work.

## Scope

This plugin supports the SRT / CLN workflow around `Srt dcf.xlsm`: new-deal
calibration, current-period registry inputs, quarterly model updates, evidence,
review readiness, conceptual SRT explanations, and the report-only copula
exhibit. It is not for CRE, CLO/CDO, consumer-pool, debt-stack, generic loan/equity
models, or client delivery approval.

## Source Of Truth

- `Srt dcf.xlsm` is the valuation model and calculation source of truth.
- Deal legal documents or approved extractions outrank model defaults.
- Prior approved methodology controls roll-forwards unless current facts make
  it impossible. Switching PD/LGD methodology is a STOP.
- Work only on copies. Edit mapped hard inputs only. Never overwrite formulas,
  named ranges, or the `Collateral` / `Notes` engines.

## Routing

Use `srt-quarterly-update` as the entry router. Keep the lane split intact:
calibration, legal mechanics, registry inputs, quarterly model update, review
package, difficulties, and copula. If a request fits one lane, answer in that
lane. If it spans lanes, answer the core question and load only the extra
reference or lane needed.

## Load Discipline

Start with `../reference-load-index.md` and load one primary reference first.
Use `model-input-cheatsheet.md` for quick cell lists and `model-cell-map.md` for
authoritative workbook detail. Do not bulk-load references.

## Non-Negotiables

- Recovery is not LGD: `LGD = 1 - recovery`; weight by RONA, never equal-weight.
- `L30` and the `L32` base are set at new-deal calibration and held fixed.
  Quarterly updates roll the benchmark change through `'Spread Analysis'!D8`,
  `L32`, and `L34`.
- `H10` is realised/liquidated severity. `H11` is estimated severity for
  defaulted but non-liquidated names and is re-marked each period.
- A defaulted name stays in the notional tie-out but is excluded from
  forward-performing PD/LGD.
- No model, report, deck, PDF, or package is client-facing until evidence and
  human approval are recorded.

## Decision Stance

- Ask for details: missing registry fields, unresolved ratings/PD/LGD, RONA
  tie-out gaps, or missing defaulted-obligor evidence.
- STOP: unclear permissions, fabrication risk, source/model mismatch, failed
  workbook checks, failed vendor refresh, methodology switch, or output that
  cannot tie back to model results.
- Optional second look: defaulted severity without a governing contract,
  benchmark selection, or how much of a spread change to embed in DM. Give the
  factors and a recommendation before noting subjectivity.

## Evidence

Every meaningful step needs an evidence record: workflow, asset class, source,
action, output/result, status, exception, owner/reviewer, and date/time when
relevant. Every mark needs a "vs. prior, because" attribution.
