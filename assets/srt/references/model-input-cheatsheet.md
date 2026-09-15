# SRT Model Input Cheatsheet

Quick cell map for analyst-facing questions. Use `model-cell-map.md` as the
authoritative reference before editing a workbook.

## New-Deal Calibration Inputs

| Cell / range | Purpose |
| --- | --- |
| `D10` | Calibration valuation date; set to `D14` |
| `D12` | Maturity / first call mapping |
| `D14` | Issue / closing date |
| `D16` | Issue price, usually par |
| `D17` | Reinvestment / replenishment end |
| `D18` | Cashflow start |
| `D19` | Payment frequency / tenor |
| `D20` | Pay at EOM |
| `D21` | Reference-rate fixing |
| `D22` | Day-count basis |
| `D23:D25` | Maturity / amortization flags |
| `D27` | Currency |
| `H3`, `H4` | Notional basis and payment lag |
| `H10:H12` | Severity and recovery lag assumptions |
| `G16:J20` | Tranche names, floating flags, margins, original balances |
| `K16:K20` | Discount-at-float flags |
| `L3` | Original portfolio balance |
| `D8` | Active tranche |
| `H36` | Clean price target/output |
| `L30` | Origination DM solve cell |

## Quarterly Update Inputs

| Cell / range | Purpose |
| --- | --- |
| `D10` | Current valuation/as-of date |
| `D11` | Last portfolio update / tape date |
| `D21` | Current SOFR/EURIBOR/base-rate fixing |
| `Inputs!C29:D82` | Discount-factor date/value table |
| `Portfolio Maturity Profile!A3:B...` | Maturity dates and current RONA |
| `H7`, `H9` | CDR and CPR scaling if updated |
| `H10` | Realised/liquidated severity if applicable |
| `H11` | Defaulted-but-not-liquidated estimated severity |
| `H12` | Recovery lag |
| `L4` | Realised/finally determined losses |
| `L5` | Defaulted-not-liquidated EAD/notional bucket |
| `L6` | Assumed-to-default bucket if used |
| `Spread Analysis!B4:B5` | Prior period spread inputs |
| `Spread Analysis!C4:C5` | Current CDS/CDX/iTraxx or single-name CDS inputs |
| `Spread Analysis!A2:C2` | Region/month labels for the spread pull |

## Preserve These Formulas

Never overwrite formulas in `D3`, `D4`, `D13`, `D15`, `D26`, `L7:L10`, `L32`,
`L34`, `M34`, `H31`, `H34:H36`, or `Spread Analysis!D4:D8`.
