---
name: srt-quarterly-model-update
description: Sub-skill routed from srt-quarterly-update — do not select directly for "quarterly SRT update" requests. Covers the in-model steps on Srt dcf.xlsm - mapped hard-input cells, valuation date roll, PD/LGD continuity, H10/H11 severity, rates/DFs, CDS / CDX / iTraxx spread changes through Spread Analysis, amortization, SES/triggers, integrity checks, and explaining mark movement.
---

# SRT Quarterly Model Update

Use this lane after calibration. Preserve prior approved methodology and anchors.

Load `../../assets/srt/references/core-contract.md`, then
`../../assets/srt/reference-load-index.md`. Work only in a copied workbook.

Checklist:

1. Confirm period, valuation date, source files, and data permissions.
2. Follow `process.md` steps 6-15 for mapped hard inputs.
3. Preserve prior PD/LGD method; unsupported method changes are STOPs.
4. Keep `H10` realised; use `H11` for defaulted/non-liquidated estimated
   severity.
5. Roll CDS / CDX / iTraxx spread change through `Spread Analysis`; preserve `D4`, `D5`, `D7`,
   `D8`, `L32`, `L34`, and `M34` formulas.
6. Do not re-solve `L30` during a quarterly update.
7. Explain movement versus prior: spread/DM, paydown, credit, date/accrual,
   methodology, and default treatment.

References: `process.md`, `model-input-cheatsheet.md`, `model-cell-map.md`,
`pd-lgd-severity.md`, `defaulted-and-nonliquidated-borrowers.md`,
`spreads-dm-calibration.md`, `dates-rates-daycount.md`.

Use `srt-review-package` for attribution, evidence, and readiness.
