# Echo — defaulted / non-liquidated borrower, then realised true-up (expected notes)

**Synthetic.** A correct run on `Spruce Logistics` (RONA $40mm, Senior Unsecured, **Defaulted, not yet
liquidated**) should produce the following, and should *reason* with
`../../references/defaulted-and-nonliquidated-borrowers.md`.

## Two principles that must both hold (and the scripts prove them)
- **Excluded from the forward-performing pool:** `pd_lgd_weighted_average.py` on the canonical registry
  reports **6 included, 1 excluded (defaulted)**, `SUM(RONA) 960` — the defaulted name does **not**
  feed go-forward PD/LGD.
- **Still in the notional / tie-out:** `normalize_tape.py` writes **7 rows**, **1 defaulted**, and the
  tie-out is **OK (1,000 = 1,000)** — the defaulted RONA stays in the reference notional until written
  down/liquidated.

## Interim — NOT yet liquidated → estimated severity (`H11`)
| Step | Value |
|---|---|
| Estimated LGD = 1 − recovery (40%) | **0.60** |
| Gross estimated loss = 40 × 0.60 | **24.0mm** |
| SES this period = 0.75% × 960 × ¼ (use-it-or-lose-it, no carry) | **1.8mm** |
| Residual to tranche = 24.0 − 1.8 | **22.2mm** |
| Equity (0–3% = 30mm) absorbs | 22.2mm → **7.8mm left** |
| **Mezz (3–7%) writedown** | **0.0mm** (but CE falls 30 → 7.8mm → credit-leg mark **down**) |

Classify as **expected loss / reserve (interim estimated protection payment)** — not a realised loss.

## Final — workout completes → realised severity (`H10`) + true-up
| Step | Value |
|---|---|
| Realised LGD = 1 − recovery (30%, worse — downturn) | **0.70** |
| Realised loss = 40 × 0.70 | **28.0mm** |
| True-up vs estimate (24.0) | **+4.0mm** (can flow either direction) |
| Cumulative loss post-SES = 28.0 − 1.8 | **26.2mm** |
| Equity remaining | **3.8mm**; mezz writedown **0.0mm** |

## Verify with your reviewer before any live use
Credit-event classification; the 40%/60% estimate vs a downturn-aware severity; whether **SES legally
applies** and on what basis; whether the name stays in notional; and whether this is booked as a reserve
vs a realised loss. The binding mark is `Srt dcf.xlsm`.
