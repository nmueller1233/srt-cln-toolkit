# The Reference Registry (CLN Trustee/Investor Report)

**Read to understand what "the registry" is and how its tabs feed the model.** On an SRT/CLN deal the
reference registry is the **trustee/investor report workbook** the deal administrator publishes each
period — obligor-level reference-portfolio data plus the period's defaults, redemptions, and capital
structure. It is the source for balances, the maturity profile, PD/LGD, and realised losses.

> **Optional local examples:** a reviewer may configure local trustee-report layout examples in
> `corpus.map.json` under `reference_examples`. Use those only to recognise the layout.
> **Do not** copy real-deal data into the portable skill. Bundled sandbox registries are synthetic
> and modelled on the expected structure.

## Workbook tabs and how each feeds the model update

| Trustee-report tab | What it holds | Feeds |
|---|---|---|
| **Current — Reference Portfolio** | Obligor-level reference pool this period (one row per reference entity). | `Portfolio Maturity Profile` (maturity + RONA) and PD/LGD weighting (`pd-lgd-severity.md`). |
| **Previous Reference Portfolio** | Prior-period pool — the quarterly update comparison. | Reconciliation; the prior balances/attach-detach. |
| **Defaulted Obligations** | Reference entities that defaulted; realised/expected loss detail. | `Inputs!L4` realised losses, `L5` defaulted-not-liquidated, the SES netting (`ses.md`). |
| **Replenished Obligations / Re-Allocations** | Substitutions during the reinvestment period. | Reinvestment-status check; pool composition. |
| **Notes Principal Payments** | Per-note redemptions: outstanding notes, available principal funds per note, partial/final redemption, notional outstanding (per note). | `Inputs!L7` repaid balance; amortisation in the maturity profile. |
| **Notes Interest Information** | Reporting/calculation/payment dates; reference rate (SOFR) + spread → note interest rate. | Cross-check the coupon and the `D21` base-rate fixing and dates. |
| **Capital Structure** | Tranche balances by portfolio reporting date. | Tranche current balances (`O16:O20`) and attach/detach recompute. |
| **Changes vs previous period** | Period-over-period movement summary. | Mark-attribution drivers (paydown, defaults). |

## Reference Portfolio columns (obligor level)

Column names vary by trustee — **do not enforce strict names**; map by meaning. Typical columns:

- **Reference entity / obligor** (and product type, entry/replenishment date)
- **Country of domicile** and **country of incorporation**
- **Industry / sector**
- **Last rating**
- **Maturity date**
- **Reference Entity Notional Amount (RONA)** — the exposure weight; the denominator for every
  portfolio-weighted figure
- **Probability of default (PD)**
- **Recovery rate** (→ LGD = 1 − recovery)
- Sometimes **seniority / secured-unsecured / lien**

## The weighting mechanic (as the registry itself does it)

The registry computes portfolio-weighted figures with RONA as the weight. The actual formula pattern
seen in the example report:

```
WA recovery = SUMPRODUCT(recovery_col, RONA_col) / SUM(RONA_col)
WA LGD      = 1 − SUMPRODUCT(recovery_col, RONA_col) / SUM(RONA_col)
WA PD       = SUMPRODUCT(PD_col, RONA_col) / SUM(RONA_col)
```

Tie `SUM(RONA_col)` back to the registry's stated total reference notional — if it doesn't reconcile,
stop; the weighting base is wrong. Details and the stratification fallback: `pd-lgd-severity.md`.

## Why this matters for the quarterly update

The whole quarterly update is "take the new trustee report and move the model to it." Maturity + RONA →
the maturity profile; defaults → realised losses (and SES netting); redemptions → repaid balance;
capital structure → current tranche balances and attach/detach. Get the registry mapping right and the
model's formulas do the rest; get it wrong and every downstream number is wrong but looks fine.
