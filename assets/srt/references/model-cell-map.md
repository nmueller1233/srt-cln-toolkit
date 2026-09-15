# Srt dcf.xlsm — Inputs Cell Map & Named Ranges

The execution map for the SRT DCF model. **HARD** = a literal input you may set; **FORMULA** = computed,
never overwrite. The model is the calculation source of truth — edit only HARD input cells, and prefer
the named range over the raw address (the host may have moved a cell).

> Derived from read-only inspection of the skeleton. Confirm a cell against the live workbook before a
> production edit — a deal may differ, and that is exactly when you stop and ask.
>
> **Workbook matching.** The HARD/FORMULA labels, formula texts and named ranges below were last checked
> against the live workbook on **2026-06-08** by `tests/srt/test_model_map_against_workbook.py` (three
> tests). On any host where `corpus.map.json` does not resolve `Srt dcf.xlsm` those tests skip. Supply the workbook to check the map against its formulas and names; the portable
> text check confirms only that the cell strings appear in this file.

**Sections:** Sheets · Checks & run controls · Dates/maturity/tenor · Collateral & loss
assumptions · Capital structure (tranche table) · Balances, DM build & results mirror ·
Discount-factor table · Inputs-vs-formulas rule · Environment artifacts to ignore.

## Sheets

`Scenarios` · `Inputs` · `_CIQHiddenCacheSheet` (CapIQ cache, ignore) · `Spread Analysis` ·
`Portfolio Maturity Profile` · `Sheet1` (scratch) · `Ramps` · `Collateral` · `Notes`.

- **Inputs** — all deal/assumption inputs, the checks, the scenario controls, and the results mirror.
- **Portfolio Maturity Profile** — the collateral amortisation/maturity engine; the quarterly update
  surface. Drives **Collateral** and **Notes** by formula — do not hand-edit those two.
- **Notes** — the note/tranche cashflow + pricing engine (where the waterfall, and any SES netting, live).
- **Spread Analysis** — prior/current benchmark and 1-month change; `D8` feeds the DM multiplier `L32`.
  Verified wiring: `D8 = D7/2` — the **÷2 dampening** of the benchmark change is in the model. The
  **units** of `B4:C5` (and so of `D8`) are not recorded here; `L32 = base + D8/100` reads very differently
  for bps than for percent, and the additive "÷2 in bps" rule in `spreads-dm-calibration.md` has not been
  established as equivalent to this wiring. Confirm the units on the supplied workbook and record its before/after DM.
- **Scenarios / Ramps** — scenario rows and CDR/CPR ramp curves (named-range sources).

## Checks & run controls

| Cell | Named range | Label | Type | Note |
|---|---|---|---|---|
| `D3` | — | Balance Check (Total) | FORMULA | `OK` ⇔ Σ orig tranche balances = orig portfolio split. **Hard stop if not OK.** |
| `D4` | — | Balance Check (Current) | FORMULA | `OK` ⇔ Σ current tranche balances = current portfolio. **Hard stop if not OK.** |
| `D6` | `ManualMode` | Manual Mode? | HARD | `TRUE` → hard `H`-column assumptions win; `FALSE` → use Scenarios row `ScenNum`. |
| `D7` | `ScenNum` | Scenario Number | HARD | Row of the Scenarios table used when not in manual mode. |
| `D8` | — | Active Tranche | HARD | The tranche being priced (e.g. `Equity`). Routes results via `H31 = MATCH(D8,Tranche_Names,0)`. |
| `H3` | — | Notional Basis for Interest Calc | HARD | `1`; coupon on original vs. outstanding notional. |
| `H4` | `Payment_Lag` | Payment Lag (Days) | HARD | Business days; **distinct from** recovery lag (periods). |

## Dates, maturity, tenor — get these right

The single most error-prone block. There are **four distinct dates**; do not conflate them.

| Cell | Named range | Label | Type | Meaning |
|---|---|---|---|---|
| `D10` | `Val_Date` | **Valuation Date** | HARD | The as-of date. **Set this each quarter.** This is the quarterly update anchor. |
| `D11` | `Last_Portfolio_Update` | Last Portfolio Update Date | HARD | Date of the portfolio tape. |
| `D12` | — | CDS Maturity Date | HARD | Note in `E12` flags **First Call Date**; distinct from legal final maturity. |
| `D13` | — | Model Maturity | FORMULA | `=D12`; the maturity the model runs to. |
| `D14` | `Issue_Date` | **Issue Date** | HARD | Origination/closing. **Not** the valuation date. The calibration anchor. |
| `D15` | `Adjusted_Issue_Date` | Adjusted Issue Date | FORMULA | EOM-adjusts `Issue_Date` if `Pay_EOM`. |
| `D16` | `Issue_Price` | Issue Price | HARD | `1` (par). |
| `D17` | `Replenishment_End_Date` | Reinvestment Period End Date | HARD | Amortisation begins only after this. Governs the reinvestment-status check. |
| `D18` | `CF_Start` | Start of CFs | HARD | When deal cashflows begin (first-funding/cashflow anchor). Fixed across rolls. |
| `D19` | `Tenor` | Tenor | HARD | `3` = quarterly, `1` = monthly. |
| `D20` | `Pay_EOM` | Pay at EOM | HARD | `TRUE`/`FALSE`. |
| `D21` | `Libor_Fix` | SOFR Fixing (Daily) | HARD | **Legacy name; holds SOFR (or EURIBOR) for the deal currency.** Update from the official source. |
| `D22` | `Daycount_Basis` | Daycount Basis | HARD | `0`=30/360, `1`=ACT/365, `2`=ACT/360. **State it on any DF/accrual change.** |
| `D23` | `Maturities_Are_Strats` | Portfolio Maturities Are Strats? | HARD | `TRUE`/`FALSE`. |
| `D24` | `Prepay_In_Amort` | Amortisation in Replenishment Period? | HARD | `TRUE`/`FALSE`. |
| `D25` | `ProRata_Amort` | Amortisation is Pro-Rata | HARD | `TRUE` = pro rata, `FALSE` = sequential. **Single deal-level flag — cannot express split/per-tranche amortisation (e.g. junior pro-rata + senior sequential); that is a STOP, see `srt-waterfall-and-triggers.md`.** |
| `D26` | `CDS_Maturity_Period` | CDS Termination Period | FORMULA | Period index of model maturity. |
| `D27` | — | Currency | HARD | e.g. `USD`; drives the fixing source (SOFR vs. EURIBOR). |

**Calibration vs. quarterly update, in one line:** at origination you solve the **Origination DM (`L30`)**
anchored to `D14`/`D18` and par (`D16`); each quarter you move the **Valuation Date (`D10`)** and the
**multiplier (`L32`)** — never the origination anchor. (`spreads-dm-calibration.md`.)

## Collateral / loss assumptions (Collateral-Modelling block)

The **active** assumption used downstream is the `I`-column formula (manual-vs-scenario switch), fed by
the `H`-column hard input when `ManualMode = TRUE`.

| Hard cell | Active (named) | Label |
|---|---|---|
| `H6` | `I6` `CDR_RampName` | CDR Ramp (e.g. `FLAT100`) |
| `H7` | `I7` `CDRScale` | CDR Scaling (e.g. `0.0025`) |
| `H8` | `I8` `CPR_RampName` | CPR Ramp |
| `H9` | `I9` `CPRScale` | CPR Scaling |
| `H10` | `I10` `Severity` | Severity (Cashflow Projection) — decimal LGD for liquidated defaults |
| `H11` | `Severity_Liquidations` | (WA) Severity (Defaulted, Not Liquidated) |
| `H12` | — | Recovery Lag (Periods) — **periods, not days** |

**Defaulted/non-liquidated bucket.** The deal's **Defaulted/Non-Liquidated tab carries the *entire*
defaulted/non-liquidated exposure at default (EAD)** — the base `H11` is applied to — and should **tie to
`L5`** (and to the registry's Defaulted Obligations tab; `registry-structure.md`). EAD **=** outstanding
notional / RONA for **funded** term exposures (the common case, so `L5`'s "notional" reads correctly), but
**= drawn + (CCF × undrawn)** for **revolvers / undrawn commitments**, where current notional understates
the base (`credit-risk-parameter-theory.md`). `H11` is the **RONA-weighted, market-
implied severity** for that bucket (set via the contract-first → comparable-price hierarchy in
`defaulted-and-nonliquidated-borrowers.md`), **re-marked each period** and **distinct from realised losses
(`L4`, severity `H10`)**, which are fixed once finally determined. *The dedicated tab is deal-specific — confirm
its name and the `L5` tie-out against the live workbook before a production edit.*

## Capital structure — tranche table (rows 16–20)

Row 16 = most senior → row 20 = most subordinated (Equity/first-loss). Leave unused rows' balances at 0.

| Col | Named range | Meaning | Type |
|---|---|---|---|
| `G16:G20` | `Tranche_Names` | Tranche names | HARD |
| `H16:H20` | `Is_Floating_Note` | Floating coupon? | HARD |
| `I16:I20` | `Tranche_Rates` | **Contractual margin (decimal — 725bps = 0.0725)** | HARD |
| `J16:J20` | `Tranche_OrigBalances` | Original balance | HARD |
| `K16:K20` | `Discount_At_Float` | Discount rate floating? | HARD |
| `L16:L20` | — (unnamed input col) | Input discount margin (decimal) | HARD* |
| `M/N/O 16:20` | `…`/`Tranche_CurrLosses`/`Tranche_Balances` | Repaid / Losses / **Current balance** | FORMULA |
| `P16:P20` | `Discount_Margin` | Model (manual-vs-scenario) DM — **the `Discount_Margin` named range lives here, on `P`** | FORMULA |

`*` `L20` (Equity DM) is itself wired `=M34` (pulls the valuation-date DM), so for the active tranche the
DM flows from the `L30`×`L32` build below rather than a hand key. Confirm per deal.

## Balances, DM build, and results mirror

| Cell | Named range | Meaning | Type |
|---|---|---|---|
| `L3` | — | Original Portfolio Balance | HARD |
| `L4` | — | Realised (Finally Determined) Losses | HARD |
| `L5` / `L6` | — | Defaulted-not-liquidated / Assumed-to-default | HARD |
| `L9` | `Current_Repaid` | Repaid incl. recoveries | FORMULA |
| `L8` | `Current_Loss` | Current losses (model) `=L4` | FORMULA |
| `L10` | `Balance` | Starting Portfolio Balance `=L3−Current_Loss−Current_Repaid` | FORMULA |
| `L30` | — | **Origination DM (bps)** — the calibrated anchor | HARD |
| `L32` | — | **Multiplier** `=96.1975% + 'Spread Analysis'!D8/100` — the `96.1975%` is a **deal-specific literal** inside the formula, set once at new-deal setup (the one sanctioned formula edit; record before/after). The contract test pins this deal's literal and must be re-pinned on another deal. | FORMULA |
| `L34` / `M34` | — | **Valuation-Date DM** `=L30×L32` (bps) / `÷10000` (decimal) | FORMULA |
| `H31` | — | Active tranche row `=MATCH(D8,Tranche_Names,0)` | FORMULA |
| `H34` | `Writedown` | **Projected Writedown** (% current bal) | FORMULA |
| `H35` / `H36` | `CleanPX` | **Clean PX** (decimal / ×100) | FORMULA |

Results-by-tranche live in rows 24–28 (`H` Factor, `I` Dirty $, `J` Accrual $, `K` Clean $,
`M` Clean PX % model current). The report lane reads these; the model-update lane captures them as
scenario outputs.

## Discount-factor table

`Inputs!C29:D82` — `C` = Date, `D` = DF. `C30 = Val_Date`, `D30 = 1`; rows 31–82 are **hard-keyed**
date/DF pairs out to ~2076. Exposed via `DF_Dates` and `DF_DFs` (OFFSET ranges). A separate live
df-curve builder sits off-screen in Inputs columns R:AK (`tbl_df_curve_*`); two of those tables point at
`#REF!` and look stale — note but don't "fix" without the analyst.

## Inputs vs. formulas — the rule

Hard inputs are the keyed values above (typically the coloured/green cells in the live file); everything
else — `Collateral`, `Notes`, the `O`-column current balances, `H34`/`H35`, `L7`/`L10`/`L32`/`L34` — is
wired. **Overwriting a formula with a hardcode silently breaks the quarterly update.** After any structural
change, re-run the checks (`D3`/`D4`) before trusting an output.

## Environment artifacts to ignore (and strip on a clean port)

`_CIQHiddenCacheSheet`, the `IQ_*` named constants, `CIQWB*`, and the `_xlpm.*` LAMBDA parameters are
Capital-IQ / Excel internals, not valuation logic. They are environment-specific noise; do not treat
them as inputs.
