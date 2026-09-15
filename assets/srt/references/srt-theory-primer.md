# SRT / CLN Theory Primer

> Orientation only. This file explains why the SRT workflow has the pieces it has. It does not set deal terms, change model formulas, or replace `legal-inputs.md`, `model-cell-map.md`, `process.md`, or reviewer approval.

## What the trade is

An SRT transfers credit risk on a reference portfolio while the bank usually keeps the loans on balance sheet. Banks do it mainly for regulatory capital relief and risk management; investors do it to earn spread for taking tranche loss risk.

A funded CLN is the common form in this workflow: the investor posts principal, receives coupon/premium, and can be written down if reference losses hit the tranche. Unfunded protection has similar loss economics but different settlement and counterparty risk.

## Reference portfolio and RONA

The registry/report defines the live pool, reference obligors, defaults, balances, and tranche structure. RONA is the exposure-weighting base for portfolio assumptions; equal-weighting obligors is wrong for tranche loss analysis.

Use `registry-structure.md` and `credit-risk-parameter-theory.md` when mapping obligor data into weighted PD/LGD/severity inputs.

## Tranching

Losses are absorbed bottom-up. Attachment is where a tranche starts losing principal; detachment is where it is wiped out. Credit enhancement is the cushion below the tranche, including subordination and any legally available SES.

Thin junior/equity pieces are highly sensitive to loss timing, severity, paydown, triggers, and market DM. The correlation/copula exhibit is report-only here and does not feed the DCF price unless the workflow explicitly says otherwise.

## How the mark forms

At a high level:

```text
registry/source data -> PD/LGD/CDR/severity inputs -> model cashflows/losses
-> SES/waterfall/tranche writedown -> DM-discounted tranche PV -> mark attribution
```

Economically, the deal exchanges a premium leg for a protection leg:

- PV premium: expected coupon/premium and principal cashflows to the investor.
- PV protection: expected loss/protection payments or CLN writedowns borne by the investor.
- The clean price/mark reflects those projected cashflows discounted at the market DM, after paydown, SES, triggers, and credit assumptions.

Quarterly movement should be attributed across rates, spread/DM, paydown, credit, structure/triggers, date/carry, and methodology when applicable. Use the operational references for the actual route: `pd-lgd-severity.md`, `spreads-dm-calibration.md`, `ses.md`, `srt-waterfall-and-triggers.md`, and `../templates/mark-attribution.md`.

## Further review

- EBA, `Report on Significant Risk Transfer in Securitisation`.
- ESRB, `The European significant risk transfer securitisation market`.
- IMF, `Recycling Risk: Synthetic Risk Transfers`.
- Deal legal documents and `Srt dcf.xlsm` model map for live mechanics.

## Where theory stops

Theory supplies vocabulary and intuition. The run is governed by the source files, legal docs, model map, workbook behavior, evidence log, and human review gate.
