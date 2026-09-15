# SRT Model — Non-Obvious Cells & House Conventions

A decoder for the handful of `Srt dcf.xlsm` cells and team conventions that
someone covering these deals would **not** already know from general
structured-credit knowledge. Generic vocabulary (RONA, PD, LGD, DM, recovery,
attach/detach, what CDX/iTraxx are) is intentionally **not** here — those are
assumed knowledge.

This is the curated "why it matters" subset, not the full cell list. For the
complete authoritative mapping use `model-cell-map.md`; for a flat quick list use
`model-input-cheatsheet.md`. Failure modes and scenarios (e.g. negative accrual)
live in `common-confusions.md`, not here.

## The DM wiring (calibrate once, roll the change)

- **`L30` — Origination DM** (HARD). The calibrated credit-spread anchor, solved
  **once** at issuance so the active tranche prints par. Never re-solved on a
  quarterly update. → `spreads-dm-calibration.md`
- **`L32` — Multiplier** (FORMULA, `= 96.1975% + 'Spread Analysis'!D8/100`). The
  single lever that moves the quarterly mark. Its base is set at new-deal setup
  and held fixed; only `D8` moves it.
- **`L34` / `M34` — Valuation-Date DM** (FORMULA, `= L30 × L32`). `M34` (decimal)
  feeds the active tranche's discount margin. This is *the* quarterly output of
  the spread roll — do not overwrite it.
- **`'Spread Analysis'!D8` — one-month benchmark change.** The only input that
  rolls the held anchor into a current mark; the quarterly spread update is, in
  effect, "get `D8` right." → `benchmark-spread-pulling.md`

## Severity, defaults, and loss buckets

- **`H10` vs `H11` — the severity split.** `H10` is **realised/liquidated**
  severity (booked). `H11` is the **estimated** severity for
  defaulted-but-not-liquidated names, re-marked each period. **Never overwrite
  `H10` / `L4` with an `H11` estimate.** → `defaulted-and-nonliquidated-borrowers.md`
- **`L4` / `L5` / `L6` — loss buckets.** Realised/finally-determined losses
  (`L4`), defaulted-not-liquidated **EAD** notional (`L5`), assumed-to-default
  (`L6`, if used).
- **EAD (defaulted/non-liquidated)** — the exposure base for the `H11` estimate,
  RONA-weighted across the defaulted/non-liquidated tab and carried in `L5`. The
  reported loss base is EAD, not pure defaulted notional.

## Dates, checks, and toggles

- **`D10` / `D14` / `D18` — the date cluster.** Valuation/as-of date, issue
  (closing) date, cashflow start. At calibration `D10 = D14`; `D18` must be
  **≤ `D10`** or the first coupon prints negative accrual. → `dates-rates-daycount.md`
  (failure mode in `common-confusions.md`)
- **`D3` / `D4` — validation checks.** Both must read `OK` before a mark is
  trusted. Preserve their formulas.
- **`D25` (within the `D23:D25` amortization flags) — the expressiveness limit.**
  `D25` cannot express split senior/junior amortization or a
  composition/sequential-trigger breach. Relying on it for those, or flipping it
  as a trigger, needs a clean modeling answer grounded in the agreement
  (per-tranche runs or an approved workaround), not a blind toggle. →
  `srt-waterfall-and-triggers.md`, `response-structures.md`
- **`H36` — clean price output.** The goal-seek target at calibration (solve
  `L30` until `H36` prints par); the priced output read each quarter.

## SES (this model)

- **SES has no input cell.** It is a **waterfall mechanic**: net it against losses
  **before** the tranche writedown, not as a number you type. → `ses.md`
