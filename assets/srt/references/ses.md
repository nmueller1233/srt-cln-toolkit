# Synthetic Excess Spread (SES)

**Read when classifying a deal for SES or running step 8.** SES varies by deal, so this is a *gate*, not
a default step — but when a deal has it, getting it wrong overstates junior-tranche losses and the mark.

## What SES is and why it matters

SES is a fixed annual spread the protection buyer commits (bp on reference notional) that is applied
against realised losses **before** they reach investors. It is effectively credit enhancement sitting
between expected loss and the first-loss tranche — it raises the *effective* attachment of the equity.
If SES is 75bp/yr and period losses annualise at 50bp, SES absorbs all of it; at 100bp, SES absorbs 75
and 25 flows to first-loss.

## The one thing to remember: SES is not an input cell

There is **no `Inputs` cell for SES.** It is a waterfall mechanic that lives in the `Notes` loss-
allocation logic. In the legal extraction it is fields **26 (excess-spread handling)** and **47 (SES
mechanism)** — both flagged "no Inputs-tab cell; describe the mechanism." So you do not "key SES in"; you
confirm the waterfall reflects it.

## The netting rule (don't double-count)

When losses are realised in a period:

1. **The full defaulted notional leaves the performing reference pool regardless** — it moves to the
   defaulted / non-liquidated bucket (`L5`), so the performing pool shrinks by the whole exposure and stops
   generating premium on it. The **loss** (defaulted notional × severity) is what is netted against SES in
   step 2; recoveries return through `H12` timing, not through the performing balance. (Corrected
   2026-09-11 to match `defaulted-and-nonliquidated-borrowers.md` and the bravo/echo sandbox keys, which
   shrink the pool by the whole defaulted notional.)
2. **Apply the loss first to the accumulated SES balance.**
3. **Only the residual beyond SES writes down the CLN notional** and hits the tranche writedown
   (`Inputs!H34`).

The two classic errors: ignoring SES (overstates tranche losses) **or** forgetting to shrink the
reference pool (overstates future premium). If SES is a fixed rate on the *current performing balance*,
**step it down** as the pool amortises/defaults.

## Sourcing SES — new deal vs. quarterly update

- **New deal:** source the SES mechanic from the deal legal document — the **rate**, the **accrual/reset
  basis**, and whether **unused SES is trapped or released** to equity. Set it up in the waterfall.
- **Quarterly update:** mirror the SES mechanics used in the prior-period DCF. If the prior figure is
  ambiguous or hard-coded, **verify it against the legal document and the reference registry** —
  reference registries frequently carry the SES figure on SES deals.
- **Source of truth is the deal document.** Some deals **reset SES by period**, so confirm the current
  period's SES against the legal terms rather than rolling a static number forward.

## Gate and evidence

- **Intake:** record SES yes/no for the deal (part of run classification).
- **Stop** if the deal carries SES but the rate / accumulated balance cannot be sourced or reconciled to
  the legal doc / reference registry — the writedown would not be source-backed.
- **Evidence:** SES rate, reset/accrual basis, accumulated balance, losses netted this period, residual
  allocated to the tranche, and the legal/registry source. (Maps to the Evidence Log; see `evidence.md`.)
