---
name: srt-difficulties
description: Use when an SRT/CLN request is conceptual: negative accrual, split amortization, EAD vs defaulted notional, CDS coupon/spread/upfront/settlement, benchmark logic, PD/LGD/recovery/severity theory, or H11/defaulted concepts. Not practical run steps.
---

# SRT Difficulties

Use this educational lane for SRT / CLN "why" questions. Give a longer theory-driven explanation; route practical steps to the lane skill.

Load `core-contract.md`, then `common-confusions.md`. Add one of:

- Negative accrued interest or calibration: `spreads-dm-calibration.md`,
  `dates-rates-daycount.md`, `model-cell-map.md`
- split-tranche amortization, SES, triggers: `srt-waterfall-and-triggers.md`,
  `ses.md`, `legal-inputs.md`
- Exposure at default, PD/LGD, recovery, severity, H11:
  `credit-risk-parameter-theory.md`, `pd-lgd-severity.md`,
  `defaulted-and-nonliquidated-borrowers.md`
- CDS coupon, On-the-run benchmark, CDX/iTraxx index constituents:
  `benchmark-spread-pulling.md`,
  `spreads-dm-calibration.md`
- newly defaulted and non-liquidated assets:
  `defaulted-and-nonliquidated-borrowers.md`
- Correlation/copula: use `srt-copula`

Answer: correction, why tempting, model/workflow tie, source needed, stance.

CDS / CDX / iTraxx alignment is not a calibration-DM suspicion test.
