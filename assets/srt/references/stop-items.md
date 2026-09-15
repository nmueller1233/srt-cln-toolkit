# Stop Items & Exceptions

**Read when something looks off.** The discipline is simple: **escalate mismatches, don't smooth them.**
A stop is not a failure — it is the control working. Log every stop in the exception log with an owner
and proposed resolution (`evidence.md`), and mark the run **not ready** until it clears.

## Host hard stops (inherited)

Stop and ask for human review if (from the control-tower rulebook):

- **Data permissions are unclear** for the run.
- A required source file is **missing**, or **cannot be tied** to the selected deal/workflow.
- The model skeleton **differs from the approved model map**.
- Workbook **formulas, links, macros, or checks fail**.
- A **vendor refresh/export/add-in fails**, or an automation lane cannot be verified.
- A report/deck/PDF output **cannot be tied back to model outputs**.
- A mismatch affects **methodology, valuation, reporting language, or client-facing output**.
- A deliverable is **ready for client use but has not had human approval**.

## SRT-specific stops

| Stop item | Why it stops |
|---|---|
| Registry cannot be tied to the deal, or `SUM(RONA)` does not reconcile to the registry total. | Balances, maturity profile, and PD/LGD would not be source-backed. |
| PD/LGD direct fields or fallback strata are ambiguous **and** the analyst's judgment is unrecorded. | Judgment is allowed, but unrecorded judgment is not evidence. |
| Deal carries SES but its rate / accumulated balance can't be sourced or reconciled to the legal doc / registry. | Tranche losses, writedown, and price would be overstated. |
| Rates / discount-factor refresh (`DF_Dates`/`DF_DFs`) is unavailable or unverified. | Discount factors and dates can't be updated with evidence. |
| SOFR/EURIBOR fixing date (`D21`) doesn't match the valuation convention. | The base-rate input would be stale or mismatched. |
| The Spread Analysis benchmark selection is unclear or unavailable. | The DM roll can't be tied to source evidence. |
| `Inputs!D3`/`D4` ≠ OK, output areas show formula errors, or named ranges/formulas are broken. | Model outputs aren't usable. |
| A tranche's price / DM / writedown moved and the driver **cannot be explained**. | An unexplained mark isn't finished — the vs-prior attribution is a required gate. |
| Reinvestment status conflicts with observed amortisation (revolving pool amortising, or vice versa). | A structural mismatch, not a rounding issue. |
| **Legal terms changed.** | The run becomes a legal-amendment / manual-review process, not a routine quarterly update. |
| A client-facing **report / deck / PDF** is requested. | Report automation is out of pilot scope until approved. |

## How to handle a stop

1. Record it in the exception log: description, severity, owner, proposed resolution.
2. If a defensible analyst judgment resolves it, **capture the judgment and the reviewer** — then proceed.
3. If not, leave the run **paused at that step** and surface it in `Exceptions / Stop Items` in the
   response. Do not carry an unresolved stop downstream.
