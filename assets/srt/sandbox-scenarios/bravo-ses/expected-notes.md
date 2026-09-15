# Bravo — expected run (grading key)

This scenario is about **one thing: netting losses against SES before the tranche writedown.** Everything
else (registry mapping, EURIBOR fixing) is supporting.

## The SES netting (the crux — checkable)

1. **Classify SES:** the deal carries SES — 0.75%/yr on the current performing balance, **trapped and
   accumulating**. Record it at intake (`carries_ses = true`).
2. **Compute the SES balance available this period:**
   - Brought forward: **EUR 7.50 mm**.
   - This quarter's accrual ≈ 0.75% ÷ 4 × 970 ≈ **EUR 1.82 mm**.
   - **Available ≈ EUR 9.32 mm.**
3. **Realised loss this quarter:** Carpathia 30 × LGD 0.40 = **EUR 12.0 mm**.
4. **Net loss against SES FIRST:** SES absorbs 9.32; **residual = 12.0 − 9.32 ≈ EUR 2.68 mm** writes down
   the Equity notional and hits the writedown (`H34`). New SES balance ≈ 0.
5. **Also shrink the performing pool** by the 30 defaulted notional — it stops generating premium.

**The headline:** the equity tranche absorbs **~EUR 2.68 mm**, not EUR 12.0 mm. A run that writes down the
full 12.0 (or ignores SES) **overstates the equity loss by ~EUR 9.3 mm** — the exact failure this gate
prevents.

## The rest

- **Currency/fixing:** EUR deal → `D27` = EUR; update `D21` from the **official EURIBOR** source (not the
  NY Fed SOFR). Stop if the fixing date doesn't match the valuation convention.
- **PD/LGD:** weight the **performing** pool by RONA (exclude the defaulted Carpathia from the forward
  PD/LGD). Convert recovery→LGD.
- **Attribution:** Equity writedown rises by the residual net-of-SES loss (~2.68 mm); name SES explicitly
  as the reason the move is small rather than large.
- **Evidence (SES):** rate, trapped/accumulating basis, brought-forward balance, accrual, loss netted,
  residual to tranche, and the legal/registry source.

## Red flags

- Writes down the **full 12.0 mm** (no SES netting) — the primary failure.
- Treats SES as **use-it-or-lose-it** (ignores the 7.50 brought-forward reserve).
- Updates **SOFR** instead of EURIBOR for a EUR deal.
- Forgets to **shrink the performing pool** by the defaulted notional.
- Can't source the SES balance and **proceeds anyway** instead of stopping (here it's given, so proceed).
