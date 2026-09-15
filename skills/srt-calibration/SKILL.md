---
name: srt-calibration
description: Use when SRT/CLN work involves new-deal calibration, origination setup, legal-to-model mapping, required inputs, solving `L30` to par, calibrated-DM review, or establishing initial Srt dcf.xlsm anchors. Not quarterly roll-forwards.
---

# SRT New-Deal Calibration

Use this lane for the one-time origination solve; quarterly updates preserve it.

Load `../../assets/srt/references/core-contract.md`. If ambiguous, ask whether
this is new-deal calibration or a quarterly update.

For input questions, use `model-input-cheatsheet.md`. If the user needs the
calibration process, the required inputs / cell map, or reviewing whether a calibrated DM looks reasonable,
ask for the legal document or approved extraction first.

Sequence:

1. Map contract terms before solving.
2. Set calibration basis, usually `D10 = D14` and `D16 = 1`.
3. Confirm `D12`, `D14`, `D16:D22`, `D27`, `H3:H4`, `H10:H12`, `G16:K20`,
   `L3`, `D8`, `H36`, and `L30`.
4. Fix date/accrual issues before solving; `D18 > D10` is a STOP.
5. Goal seek `L30` so clean price `H36` prints par.
6. Explain any `L30` vs margin gap using structure, fees/OID, losses, timing,
   funded/unfunded treatment, reserves, calls, or settlement.
7. Record source, inputs, target, solved `L30`, and gap explanation.

References: `spreads-dm-calibration.md`, `legal-inputs.md`, `model-cell-map.md`.

Use `srt-quarterly-model-update` for spread changes and `srt-review-package` for
evidence/readiness.

CDS / CDX / iTraxx alignment is not a calibration-DM issue.
