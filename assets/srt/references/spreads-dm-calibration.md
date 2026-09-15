# Discount Margin: Calibration & the Spread Analysis Roll

**Read for the new-deal calibration, the quarterly DM roll, and how the Spread Analysis tab actually
wires into the price.** Discount margin (DM) is the spread over the floating benchmark (SOFR/EURIBOR)
that makes PV = price — the natural, primary measure for a floating SRT tranche. "SOFR + 450" → 450 is
the DM.

## How the DM is built in the model (the real wiring)

Three cells, two of them formulas — do not overwrite the formulas:

| Cell | What | Type |
|---|---|---|
| `L30` | **Origination DM** (bps) — the calibrated anchor, solved once at issuance | HARD |
| `L32` | **Multiplier** `= 96.1975% + 'Spread Analysis'!D8/100` | FORMULA |
| `L34` / `M34` | **Valuation-Date DM** `= L30 × L32` (bps) / `÷10000` (decimal) | FORMULA |

`M34` feeds the active tranche's discount margin (e.g. Equity `L20 = M34`). So the quarterly mark moves
through **one lever — the multiplier `L32`** — driven by **`'Spread Analysis'!D8`** (the one-month
benchmark change). The origination anchor `L30` does not move on a quarterly update.

> **Workbook and shadow conventions.** Two statements of the roll
> serve different calculations in this toolkit; their equivalence requires confirmation against the supplied workbook: (a) the verbal rule
> below and `shadow_run.py` — "benchmark change ÷ 2, **added** to the previous DM in bps"; (b) the wiring
> above — `L34 = L30 × (base + D8/100)`, which is **multiplicative and scaled by `L30`**. Read literally with
> `D8` in bps, (b) moves the DM by `L30 × D8/100` (≈ 22 bps for `D8 = −4` at `L30 = 553`), not by 4 bps,
> and it is not path-dependent (a flat month returns the DM to `L30 × base`). Confirm the units of `B4:C5`/`D8`
> on the supplied live tab. Until they are confirmed, treat the ÷2 rule as the *documented*
> adjustment and the shadow harness as its additive form, and record the before/after `L34` each quarter.
> The base `96.1975%` inside `L32` is a **deal-specific literal** set once at new-deal setup (see below).

### Rates vs. spread — it's a floater (attribution)

The tranche pays a **floating** coupon that **resets** to the benchmark, so its price is largely
**insensitive to the benchmark *level*** — the **rates leg of a mark move is ≈ 0 while the tranche is near
par with small projected losses** (a discounted or heavily written-down tranche does carry rate sensitivity:
the DM-minus-margin gap and the fixed projected loss are both discounted at the benchmark). What moves the mark
is the **discount margin (the credit-spread leg)** — the `L32`/`L34` roll above. So in a mark-attribution
bridge, do **not** book a benchmark move under "rates"; it is a **spread / DM** effect. Only the
discount-factor *curve* refresh and accrual/day-count touch the rates/date legs (`dates-rates-daycount.md`).

## New-deal calibration (solve the anchor to par)

A tranche bought at par on day one must value to par that day. Calibration records that risk profile so
future valuations preserve it while the market moves.

1. Set the valuation date to issuance (`D10` = issue), issue price = par (`D16` = 1). *This sequence
   assumes the tranche was issued at par; a deal sold with OID or at a premium requires a separately specified calibration sequence.*
2. **Goal Seek the Origination DM (`L30`) so the clean price (`H36`) prints par.** (Confirm the exact
   Goal-Seek target cell against the live workbook — the multiplier construction means you want clean
   price at par for the active tranche at issuance.) **Record two things in the calibration evidence:**
   (i) the value of `L32` at the moment of the solve — `L30` is only the day-one DM if the multiplier was
   100 % then, since only the product `L30 × L32` enters the price; (ii) which collateral inputs
   (Portfolio Maturity Profile, `H7` CDR scaling, `H10`/`H11` severity, SES, DFs) were the deal's own at
   the time of the solve, because the par solve prices the *projected* cash flows and a template that
   still carries another deal's assumptions anchors `L30` to those assumptions.
3. **Sanity-check** the calibrated `L30` against the contractual margin (`I`-column, decimal). On a
   par-funded floating deal with no fees/base-case losses they should be close (~within 10bp). If they
   diverge, name why: upfront fees/OID push DM **up**; aggressive base-case losses push it **down**.
4. **Calibrate once.** Never re-solve `L30` on a quarterly update — that would erase the origination anchor.
5. **Derive the multiplier base (new-deal key step).** After `L30` is solved, set the **base** of the
   multiplier `L32 = base + 'Spread Analysis'!D8/100` so the model **clean price `H36`** equals where the
   tranche actually prices given current market levels — judged from **comparable new-issue spreads/coupons**
   on the same shelf (the model keeps these next to the multiplier, e.g. `N32/N33` comparable new-issue coupons). Goal
   Seek `L32` so `H36` hits that comp-implied price and read off the base; **record the comparables and the
   target price**. The base is then **held fixed on quarterly updates** — only `D8` moves it (the one exception
   is a trade printing on the deal). What the multiplier is, how it's derived, and why, lives in
   `benchmark-spread-pulling.md` ("The multiplier").

### Failure mode: negative accrued interest from a mis-set cashflow start (check before you trust the solve)

Calibration forces the **valuation date `D10` = `Issue_Date D14`** and Goal-Seeks `L30` so clean price
prints par. The accrued-interest figure (`J24:J28`, "Accrual $" = dirty − clean) is computed as the
day-count fraction **from the most recent scheduled coupon date to the as-of date**, and the coupon
schedule is anchored at **`D18 CF_Start`** stepped by **`D19 Tenor`**.

- If **`CF_Start (D18)` is set *after* the issue/valuation date**, the nearest scheduled accrual-start the
  model finds lands in the **future** relative to `D10`. The elapsed fraction `(Val_Date − accrual_start)`
  goes **negative**, so `J` prints **negative accrued interest**, dirty < clean, and the DM Goal-Seek
  calibrates `L30` against a malformed first coupon — a wrong anchor that then rides through every roll.
  **This is the case that produces a negative number.**
- The mirror case — **`CF_Start` *before* the issue date** — does *not* go negative; it produces a
  *spurious-positive* phantom accrual (the model accrues a stub before the note was funded). Still wrong,
  just the opposite sign.

**Gate:** before trusting a calibration solve, eyeball the `J`-column accrual. A **negative** accrual is a
**STOP** — the fix is `D18 ≤ D10`, with the first scheduled coupon ≥ `D14 Issue_Date`, not a different
`L30`. Re-solve `L30` only after the dates align. State the basis (`D22`) and the three dates in evidence.
Confirm the accrual sign behaviour against the live `Notes`-sheet engine — the exact formula lives there.

## Quarterly DM roll (the Spread Analysis tab)

The `Spread Analysis` tab holds *prior month*, *current month*, and the *one-month change* (`D8`), and
`D8` is what feeds the multiplier `L32`. Each quarter:

1. **Move the prior period's current spreads into the previous-period column.**
2. **Pull this period's CDS / CDX / iTraxx spread input** from the approved source, choosing the source
   by the tranche's collateral/currency.
3. **Apply the dampened change** to the previous-period midpoint DM / multiplier:
   - **basis-point change ÷ 2** — this is the form the workbook computes (`D8 = D7/2`, `D7 = C − B` in bps).
   - A "percentage change ÷ 4" form is sometimes quoted for the same step. It is **not** the same
     adjustment: `Δb/2 = DM × (Δb/b)/4` only when `DM = 2 × b` (the DM is exactly twice the benchmark
     level). Do not use it; apply the bp form once. (Corrected 2026-09-11.)

### Why the dampening (record this each period)

The roll is a **muted** application of the benchmark move, not a one-for-one pass-through: a single
period's benchmark print carries noise, and the midpoint DM should not chase it fully. The appropriate
degree of dampening **scales with the size of the tranche coupon and the volatility of the CDS
benchmark** — a thin, high-coupon equity piece against a noisy benchmark warrants more muting than a
tight senior. Record, every period: the **benchmark chosen**, the **raw change**, the **factor applied**,
and the **before/after DM**. A reviewer must be able to reproduce the after-DM from the saved CapIQ
inputs and the previous-period DM — if they cannot, the spread roll is not evidenced.

## Gates and evidence

- **Stop** if the benchmark selection is unclear or the source is unavailable — the roll cannot be tied
  to evidence.
- **Evidence:** prior/current CDS / CDX / iTraxx spread inputs, approved source, raw change, dampened adjustment with its
  recorded rationale, and the before/after DM (or multiplier) bridge. For a new deal: the par-solve and
  the `L30`-vs-contractual-margin gap with its explanation.
