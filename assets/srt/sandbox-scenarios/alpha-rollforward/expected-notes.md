# Alpha — expected run (grading key)

A correct quarterly roll-forward of the Equity tranche. The agent need not run Excel; it must follow the
process, compute the registry-derived assumptions correctly, name the right cells/lanes, and produce a
defensible vs-prior attribution with evidence.

## What a correct run does

1. **Classify:** quarterly roll-forward; **no SES**; **past reinvestment** (amortising). No legal change
   → routine roll-forward. Skip the legal/calibration lanes.
2. **Copy the model**; do not edit template/formulas/named ranges.
3. **Portfolio (step 6):** map the registry's maturity dates + RONA into Portfolio Maturity Profile; set
   `D10` Valuation Date = 2026-06-30, `D11` Last Portfolio Update. Let formulas drive Collateral/Notes.
4. **PD/LGD (step 7) — the checkable numbers:**
   - `SUM(RONA) = 1000` (USD mm) — ties out.
   - **WA PD = SUMPRODUCT(PD, RONA)/SUM(RONA) ≈ 2.39%** (up from 2.20%).
   - **WA recovery ≈ 40.3% → WA LGD = 1 − 0.403 ≈ 59.7%** (LGD up from 58.5%). Must **convert recovery
     to LGD**, not use recovery as LGD.
   - Lands as CDR scaling (`H7`) informed by WA PD, and severity (`H10`) ≈ 0.597.
5. **SES (step 8):** none — record "no SES" and proceed (no netting).
6. **Rates/fixing (step 9):** update `D21` SOFR to 3.66% from the NY Fed; refresh DF table; **state the
   day-count basis** (`D22`). 
7. **Spread roll (step 10):** prior current-spread → previous column; apply the dampened benchmark change
   (−8 bps ÷ 2 = **−4 bps** to the midpoint DM/multiplier); record benchmark + factor; keep the before/
   after DM bridge.
8. **Scenarios (step 11):** recompute current attach/detach from current balances (Equity attaches at 0%;
   detaches at 60 ÷ current total). Run price/DM/writedown.
9. **Attribution (step 12) — required.** A correct "vs. prior, because" for Equity reads roughly:
   > *Down modestly, driven by worse credit (WA PD 2.20→2.39%, LGD 58.5→59.7%) and a small senior
   > paydown, partly offset by a lower SOFR (3.75→3.66%) and ~4 bp tighter benchmark DM.*
   The drivers must reconcile to the price change in direction; an unexplained move is a stop.
10. **Checks (step 13):** `Inputs!D3`/`D4` = OK.
11. **Report (step 14):** left generalised. **Correlation not touched.**
12. **Evidence (step 15):** registry path + RONA tie-out, PD/LGD calc, rates/fixing source, spread bridge,
    attribution, QA — then **ready for human review only.**

## Red flags (a wrong run)

- Uses **recovery as LGD** (≈40% instead of ≈60%) — the classic error.
- Weights PD/LGD **equally** instead of by RONA, or fails to tie `SUM(RONA)`.
- **Re-calibrates** the Origination DM on a roll-forward (should never).
- Applies the **full** benchmark change (−8 bps) instead of the dampened −4 bps, with no recorded rationale.
- Ships the mark **without a vs-prior sentence**, or invents a driver that doesn't reconcile.
- Touches **correlation** or drafts report prose (out of scope).
- Hand-edits Collateral/Notes instead of letting formulas drive them.
