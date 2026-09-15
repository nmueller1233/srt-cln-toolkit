# SRT Waterfall, Triggers, and Attachment Movement

> Guidance only. This file explains loss/principal flow and attribution. Binding mechanics live in the deal documents, `legal-inputs.md`, `model-cell-map.md`, `ses.md`, and the workbook.

## Loss path

Use this order:

1. The full defaulted notional leaves the performing pool (into the defaulted / non-liquidated bucket);
   future premium should not be earned on defaulted exposure. The loss on it is what step 2 nets.
2. SES absorbs first only if the deal legally provides it. `ses.md` controls availability and netting.
3. Residual loss writes down the CLN/tranche bottom-up and feeds the model writedown line (`Inputs!H34`).

Skipping step 1 overstates premium. Skipping SES overstates tranche loss.

## Principal waterfall

| Mode | Principal paid | Typical effect |
|---|---|---|
| Pro-rata | Across tranches proportionally | Leverage roughly maintained |
| Sequential | Senior first | Senior de-levers; junior/equity extends and retains more loss exposure |

Many deals start pro-rata and flip to sequential after a trigger breach, but the legal document controls.

## Triggers

Common trigger families include OC, IC, cumulative-loss/default, and portfolio-composition tests such as CCC/Caa concentration, industry concentration, top-N obligor concentration, or WARF/quality limits.

For composition triggers, the registry must contain the fields needed to compute the test. If rating, industry, obligor, or notional fields are missing, stop; do not assume the trigger passes.

When a trigger flips the structure:

- Update the model route if the workbook can represent it.
- Attribute the mark movement to structure/waterfall.
- Stop for review if the trigger, cure provision, or required source field is unclear.

## Split amortization vs `D25`

Some deals amortize different tranches differently. The model has a single deal-level switch, `D25 ProRata_Amort` (`TRUE` = pro-rata, `FALSE` = sequential). If the structure is genuinely split by tranche, one flag cannot represent both sides.

Do not pick a convenient `D25` value and continue. Escalate the model-expressiveness gap and agree a representation, such as separate runs, a documented workaround, or an approved model change.

## Attachment and detachment movement

Attachment/detachment move with current balances:

```text
attach = subordinate current balance / current total
detach = attach + tranche current balance / current total
```

Sequential senior paydown can raise credit enhancement for senior tranches while starving juniors. Realised writedowns can erode subordination. Pool amortization changes the denominator. Recompute each period from current balances and attribute meaningful movement.

## Mark attribution

A mark should explain the change vs prior across the relevant drivers: rates, spread/DM, paydown, credit, SES, trigger/waterfall, attachment movement, methodology, and date/carry. Use `../templates/mark-attribution.md`; `spreads-dm-calibration.md` owns the spread leg.

## Further review

- Deal indenture/confirmation for the actual waterfall, triggers, cure language, and SES use.
- EBA materials on SRT and non-sequential amortisation trigger expectations.
- BCBS securitisation framework notes for waterfall and credit enhancement context.

## Where this file stops

The legal documents and workbook determine the actual waterfall, trigger tests, cure mechanics, SES use, and model representation. Stop on unexplained structure changes or unsupported source fields.
