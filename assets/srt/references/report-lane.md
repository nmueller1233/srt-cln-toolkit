# Report Lane (Out of Pilot Scope)

**Read only to understand the report lane — do not automate it in the pilot.** The model-update pilot
stops at scenario outputs + evidence. Report drafting, exhibits, correlation outputs, and any
client-facing package are **excluded** until separately approved. This reference exists so the boundary
is clear and so a future report module has a faithful starting point.

## The two-file pipeline

The report lane is two chained prompts (both run by a human in the approved enterprise tool):

1. **Extraction prompt** (`SRT Report Update Prompt v2`) — reads the model's **`Inputs` tab only**
   (explicitly not Scenarios/Collateral/Notes) and emits the report variables in six sections:
   A Deal Overview · B Capital Structure · C Collateral Performance · D Key Assumptions ·
   E Single-Scenario Outputs · F Results by Tranche.
2. **Drafting prompt** (`SRT Report`) — consumes the extraction output and drafts the report:
   1 Header · 2 Exhibit label · 3 Investment Overview (prose) · 4 Transaction Overview & Key Terms
   (4A Capital Structure, 4B Key Terms, 4C Assumptions) · 5 Concluded Fair Value table · 6 Commentary
   (prose) · 7 Conclusion.

## Output variables (where they come from)

- **Deal overview / key terms:** `D10` Val Date, `D14` Issue Date, `D12` maturity (call vs final),
  `D13` model maturity, `D17` reinvestment end, `D18` CF start, `D27` currency, `D8` active tranche,
  `L3` original portfolio balance.
- **Capital structure / attach-detach:** tranche rows 16–20 — names, original/current balances, losses,
  repaid, contractual margin (report as "SOFR + X%"), DM. Attach/detach computed from balances (current
  attach = Σ subordinate **current** balances ÷ **starting** portfolio balance).
- **Assumptions:** CPR (`H9` scaling), CDR (`H7` scaling), severity (`H10`), recovery lag — take the
  "Single Scenario" column.
- **Outputs:** projected writedown (`H34`), clean price (`H35`/`H36`), valuation DM (`L34`), origination
  DM (`L30`), WAL, multiplier (`L32`). The only hard cell coordinates the prompt names are inputs `D12`
  / `L20` and outputs `H35` / `H34` (used to read each maturity/DM scenario).

## Correlation in the report (the only place it appears)

Correlation is **a per-scenario model-type label** — each scenario is tagged "DCF" or "Correlation," and
the fair-value range may blend DCF and Correlation-model scenario prices. There is **no correlation input
cell and no correlation exhibit** defined in the report prompts; the Gaussian-copula workbook is what
produces a correlation scenario when one is used. This matches the standing rule: **the DCF mark does not
depend on correlation**, and the model-update pilot ignores it. The analyst does not compute correlation;
do not add it to the pilot.

## Why it's out of pilot

Report prose, the fair-value exhibit, and client-facing assembly carry methodology and language risk and
are "ready for client use" artifacts — exactly the host hard-stop category. Keep the report **generalised
and awaiting data**; log it as an open item, not a blocker.
