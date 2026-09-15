# Credit-Risk Parameter Theory (PD, LGD, Recovery, Severity, EAD)

> Guidance only. This file explains parameter meaning and common mistakes. It is not a pricing engine and does not override the registry, legal documents, `pd-lgd-severity.md`, `model-cell-map.md`, or the live workbook process. For valuation/routing, load the operational reference that owns the step.

## Parameters to keep distinct

| Term | Meaning | Model use |
|---|---|---|
| PD | Probability an obligor defaults over a stated horizon | Informs CDR/loss projection; horizon must match the run |
| Recovery | Fraction of exposure recovered after default | Convert before use: `LGD = 1 - recovery` |
| LGD | Fraction lost after default | Same economic concept as severity |
| Severity | Model label for LGD | `H10` for realised/liquidated, `H11` for defaulted/non-liquidated |
| EAD | Exposure at default, the loss base | Usually RONA for funded term exposure; confirm revolvers/undrawn commitments |

Guardrails:

- Recovery is not LGD. A 40% recovery is a 60% LGD/severity.
- Percent/decimal errors break the mark. Use `0.40` or `40%`, not `40`.
- PD must carry a horizon. A one-year PD is not a lifetime PD.
- For funded term loans/bonds, EAD normally equals current RONA. For revolvers, EAD may include expected future draws; stop if the registry is ambiguous.

## RONA weighting

Portfolio assumptions are exposure-weighted:

```text
WA PD  = sum(PD_i * RONA_i) / sum(RONA_i)
WA LGD = 1 - sum(recovery_i * RONA_i) / sum(RONA_i)
```

Equal-weighting treats a small obligor like a large one and can materially misstate tranche loss. Tie `sum(RONA)` to the registry before trusting any weighted figure.

## Current default vs future default

- Expected/forward loss applies to performing names.
- A current default is no longer a future default candidate.
- Realised/liquidated losses use fixed severity in `H10`.
- Defaulted but non-liquidated names use estimated severity in `H11`, re-marked until the loss is final.

Do not count a name both as a realised/defaulted loss and as part of the forward-performing PD pool. Use `defaulted-and-nonliquidated-borrowers.md` for that route.

## Spread and DM intuition

Historical PD/LGD explain the loss projection. Market spread/DM explains the discount leg. A spread move should usually be attributed through the DM route, not by forcing PD/LGD to absorb a market move.

The exact calibration and quarterly update wiring lives in `spreads-dm-calibration.md`, including `L30`, `L32`, `L34`, CDS/CDX/iTraxx alignment, and multiplier theory. This file only supplies vocabulary so those mechanics are not confused.

## Further review

- GARP/FRM materials on PD, LGD, EAD, and default probability.
- BCBS IRB framework notes for downturn LGD and EAD/CCF concepts.
- O'Kane, `Modelling Single-name and Multi-name Credit Derivatives`, for credit spread/DM intuition.

## Where this file stops

Use this reference to avoid parameter mix-ups. Use `pd-lgd-severity.md`, `defaulted-and-nonliquidated-borrowers.md`, `spreads-dm-calibration.md`, `registry-structure.md`, and `model-cell-map.md` for actual run decisions. If the source, model map, or legal doc conflicts with this primer, escalate the mismatch.
