# Charlie — expected run (grading key)

A new-deal setup. The point is the **field→cell mapping** and the **calibration to par** — not a
roll-forward. The legal lane is source-only; calibration runs once.

## What a correct run does

1. **Classify:** new-deal setup (not a roll-forward). Legal extraction is **manual/source-only** — the
   agent documents the mapping and flags that a human extracts/approves before values go live.
2. **Map fields → cells** (decimal where required):
   - Dates: `D14` 2026-05-15, `D18` 2026-05-21, `D12` 2031-05-21 (First Call), legal final 2034-05-21
     captured separately, `D17` 2029-05-21, `D19`=3, `D22`=2, `D20`=FALSE, `D27`=USD, `D16`=1.
   - Tranches rows 16–20: names `G`, floating `H`, **margins `I` in decimal** (Senior 0.0110, Mezz
     0.0450, Equity **0.0900**), original balances `J` (1,840 / 100 / 60).
   - `D25`=TRUE (pro rata) with the 5% cumulative-default sequential trigger noted (narrative, no cell).
   - SES 0.50% use-it-or-lose-it recorded (mechanism; no input cell).
3. **Calibrate (step 5):** set the valuation date to issuance (`D10` = 2026-05-15), issue price par
   (`D16` = 1), and **Goal Seek the Origination DM (`L30`) so the Equity clean price (`H36`) prints par.**
   Confirm the exact Goal-Seek target against the live workbook.
4. **Sanity-check:** the calibrated `L30` should sit **near the Equity contractual margin (900 bps)**
   absent fees/OID/base-case losses; name any gap (fees push DM up; aggressive base-case losses push it
   down). On a par-funded floating deal they should be within ~10 bp.
5. **Do not re-solve** the Origination DM later — calibration happens once at issuance.
6. **Evidence:** legal source + reviewer note; the par-solve; the `L30`-vs-900bps gap with explanation.

## Red flags

- Treats this as a **roll-forward** (rolls a spread, refreshes a prior mark) instead of calibrating.
- Leaves **margins in bps** (e.g., 900) where the model wants decimal (0.0900), or double-converts.
- Maps **issue date to the valuation anchor** or confuses `D14`/`D18`/`D12` (issue vs CF-start vs call).
- **Automates** the legal extraction instead of treating it as manual/source-only with human review.
- Calibrates to a number **far from 900 bps** without explaining why (a silent mis-calibration).
