# Dates, Base-Rate Fixing, Day Count & Discount Factors

**Read for the valuation-date convention, the SOFR/EURIBOR fixing, day count, and the discount-factor
refresh.** These are quiet, high-leverage error sources — a wrong date or day-count silently moves the
whole curve.

## The four dates (don't conflate them)

| Cell | Named range | Role |
|---|---|---|
| `D10` | `Val_Date` | **Valuation / as-of date — set each quarter.** The quarterly update anchor. |
| `D14` | `Issue_Date` | Origination/closing. The **calibration** anchor (not the val date). |
| `D15` | `Adjusted_Issue_Date` | EOM-adjusted issue date (formula). |
| `D18` | `CF_Start` | When deal cashflows begin (first-funding/cashflow anchor). Fixed across rolls. |

Also `D11` `Last_Portfolio_Update` (the tape date) and `D12`/`D13` maturity (call vs model maturity).

## Month-end valuation convention

Use the **calendar month-end** as the as-of date even when it falls on a weekend/holiday:

- Val-date *label* = last calendar day of the month.
- **Market data = last available business-day close** (e.g. the prior Friday).
- Accrued interest, paydowns, and date-driven items calculate through calendar month-end.
- Caveat: confirm against the deal's prior quarterly updates — some deals set the date itself to the prior
  business day. Calendar-last-day is the default for month-end reporting unless the deal says otherwise.

## Base-rate fixing (`D21`, `Libor_Fix`)

`Inputs!D21` is labelled **"SOFR Fixing (Daily)"** and named **`Libor_Fix`** — the name is legacy; the
cell holds the deal's actual benchmark.

- Update from the **official source** matching the deal currency (`D27`): **SOFR from the New York Fed**;
  **EURIBOR from the official EMMI/euribor source** for EUR deals. Use the deal's exact rate formulation
  (Daily vs Term vs compounded-in-arrears) as captured at extraction.
- **Record** the source URL, the fixing date, and the value.
- **Stop** if the source/fixing date does not match the valuation convention — a stale or mismatched
  fixing quietly biases every coupon.

## Day count (`D22`, `Daycount_Basis`)

Encoded numerically: **`0` = 30/360, `1` = ACT/365, `2` = ACT/360.** Day count is a top-tier
calibration/accrual error — **state the basis explicitly** on any discount-factor or accrual change, and
confirm it matches the legal doc. An ACT/360-vs-365 mismatch typically pushes the calibrated spread the
wrong way by a few bp.

## Discount factors (`C29:D82`)

`Inputs!C29:D82` — `C` = Date, `D` = DF; `C30 = Val_Date`, `D30 = 1`; rows 31–82 are **hard-keyed**
date/DF pairs out to ~2076, exposed via the named ranges **`DF_Dates`** and **`DF_DFs`**.

- Refresh from the **approved rates workbook** (Refinitiv/LSEG plug-in lane) and update the date/DF
  table where the DFs are formulaically calculated. **Preserve the model's formula methodology** — do
  not paste over the wiring.
- A separate live df-curve builder sits off-screen in Inputs cols R:AK (`tbl_df_curve_*`); two of those
  tables point at `#REF!` and look stale. Note it; don't "fix" without the analyst.
- **XNPV/XIRR note:** the model's IRR uses `XIRR` (`M39`). Wherever a value is built with XNPV/XIRR, the
  **first date is the as-of anchor with a zeroed flow** (DF = 1) — nothing is paid *on* the val date, so
  leaving a real cashflow there adds an undiscounted phantom at t = 0.

## Evidence

Rates refresh export; base-rate source URL + fixing date + value + currency/convention; the Inputs
date/DF table before and after; and the day-count basis used. **Stop on any unverified vendor refresh.**
