# SRT Quarterly Model-Update — Full Process

The step-by-step quarterly update for `Srt dcf.xlsm`. Platform-neutral: the **Lane** column uses the host's
automation-lane vocabulary (manual / power_query / vendor_addin / excel_vba / power_automate_desktop /
python_runner), and each step names the evidence it must leave. Lead with the action; preserve the model.

**Cell references are summarised inline; the authoritative map (input vs. formula, named ranges) is
`model-cell-map.md`. Read it before touching cells.**

## 0. Classify the run first

- **Quarterly update** (same deal, new period, no legal change) -> run steps 1-15, skipping 4-5.
- **New deal** → run 1–3, then 4 (legal, source-only), then 5 (calibrate), then 6–15.
- **Legal amendment** -> contractual terms changed; this is **not** a routine quarterly update. Legal
  extraction is manual/source-only and needs human review before any contractual input enters the model.

## The steps

| # | Action | Lane | Evidence / Gate |
|---|---|---|---|
| 1 | **Confirm run context**: deal/test case, period end, frequency, target folder, **data classification**, available sources, expected outputs, manual constraints. Add SRT classifiers: run type; SES yes/no; in vs. past reinvestment; currency/reference rate. | manual | Run intake record. **Stop if data permissions are unclear.** |
| 2 | **Create a current-period copy** of `Srt dcf.xlsm` in the period folder. Do **not** alter the template, core formulas, named ranges, the `Collateral`/`Notes` engines, or the copula workbook. | manual / power_automate_desktop | Source-model copy path. |
| 3 | **Classify the run** (quarterly update / new deal / legal amendment). Legal changes leave the routine lane. | manual | Classification in run state. |
| 4 | *(New deal / amendment only)* **Map legal fields** using the extraction prompt + legal-to-model map. Keep extraction **manual and human-reviewed**; never automate it. | manual (source-only) | Legal source + reviewer approval. → `legal-inputs.md` |
| 5 | *(New deal only)* **Calibrate**: set the valuation date to issuance, keep issue price = par (`D16`=1; the sequence assumes a par issue), and solve the **Origination DM (`L30`)** so the clean price prints par. Sanity-check `L30` vs. the contractual margin and explain the gap (fees/OID/base-case loss). **Then derive the multiplier base**: the base is the **literal inside the `L32` formula** (`=96.1975% + 'Spread Analysis'!D8/100`), so Goal Seek cannot target it directly — solve for the base value that makes clean price `H36` match where the tranche prices vs. **comparable new-issue spreads/coupons**, then set that literal once (the one sanctioned formula edit at new-deal setup; record before/after); record the comps + target price. The base is **held fixed on later quarterly updates** (only `D8` moves it; a trade is the rare exception). **Inputs at calibration:** the par solve prices the projected cash flows, so it is only the deal's day-one DM if the deal's own Portfolio Maturity Profile, `H7`/`H10`/`H11`, SES and DFs (steps 6–9) are already in the copied template; record which inputs were in place at the solve, and re-solve with a documented reason if they change afterwards. | excel_vba (Goal Seek) | Calibration evidence: par solve (with `L32` and the collateral inputs in place recorded), DM-vs-margin gap explained, **multiplier-base derivation (comps + target price)**. -> `spreads-dm-calibration.md`, `benchmark-spread-pulling.md` |
| 6 | **Update Portfolio Maturity Profile** from the latest registry: build the maturity-date + current-RONA profile; let model formulas drive `Collateral`/`Notes` (do **not** hand-edit those). Set `D10` Valuation Date, `D11` Last Portfolio Update; record reinvestment status (`D17`). | power_query / manual | Registry path, column mapping, RONA tie-out, reinvestment status. |
| 7 | **Update PD and LGD/severity. FIRST read last quarter's methodology for this deal** (prior run-state / evidence / mark-attribution) and **stay consistent** — but do not replicate a prior mistake; if you correct one, attribute the correction so the move isn't read as risk. Then follow the path the deal was calibrated on: **obligor-level** registry PD/LGD (RONA-weighted) if that's the calibrated method and the tape provides them, **else aggregate** the registry into the CLN performance curve. **Switching methods is a STOP for human review** (it injects a methodology-driven mark variance). Convert recovery→LGD first. Lands in the Collateral-Modelling block (`H7` CDR scaling, `H10`/`H11` severity, etc.). | excel_vba / python_runner | Prior-methodology note; PD/LGD calc or CLN aggregation; S&P snapshot if fallback used. → `pd-lgd-severity.md`, `cln-aggregation.md` |
| 7a | **Set defaulted / non-liquidated severity (`H11`)** — for the names on the defaulted/non-liquidated tab (not the performing pool). Work **per obligor, top-down**: **contract first** (contractual / fixed recovery, unless the client gives borrower-level insight); else **Debtwire** material-change research (restructuring / distressed exchange, missed payment, bankruptcy) **+** the **secondary price of the most comparable bond** as a market-implied recovery (match seniority / lien / sector / tenor). **RONA-weight across the tab** → `H11 = 1 − WA recovery` (prices as a fraction of par). It applies to the **whole defaulted/non-liquidated EAD** on the tab (= notional for funded exposures; `drawn + CCF×undrawn` for revolvers) and is an **estimate re-marked each period — distinct from realised loss (`L4` / `H10`)**; don't overwrite a crystallised loss with it. | python_runner / manual | Per-name: contract clause or comps + secondary price + date; Debtwire citations; RONA tie-out to the tab (→ `L5`). → `defaulted-and-nonliquidated-borrowers.md`, `pd-lgd-severity.md` |
| 8 | **SES gate** *(deal-dependent)*: if the deal carries synthetic excess spread, confirm period losses net against the accumulated SES balance **before** any tranche writedown; only the residual writes down notional. If no SES, record that and proceed. | manual / excel_vba | SES classification + netting evidence. → `ses.md` |
| 9 | **Refresh discount factors** (`Inputs!C29:D82`, named `DF_Dates`/`DF_DFs`) from the approved rates workbook, and **update the daily base-rate fixing** (`D21`, named `Libor_Fix` — holds SOFR/EURIBOR despite the legacy name) from the official source. **State the day-count basis** (`D22`). | vendor_addin (human lane) | Rates refresh evidence; NY Fed / EURIBOR source URL, date, value; before/after DF table; day-count. **Stop on unverified refresh.** → `dates-rates-daycount.md` |
| 10 | **Roll Spread Analysis forward**: prior current-spreads move to the previous-period column; pull this period's benchmark from the approved source; apply the dampened change to the multiplier. The multiplier feeds `L32 = 96.1975% + 'Spread Analysis'!D8/100`, and `L34 = L30 × L32` is the valuation-date DM. | vendor_addin (human lane) | Benchmark evidence + before/after DM bridge. → `spreads-dm-calibration.md` |
| 11 | **Recompute current attachment/detachment** from current balances (current attach = subordinate current balance ÷ current total; detach = attach + tranche current balance ÷ current total), then **run the required price/DM/writedown scenarios** via the scenario engine (`D6` ManualMode, `D7` ScenNum, `D8` Active Tranche; outputs `H34` Writedown, `H35/H36` Clean PX). Exclude correlation and report drafting. | excel_vba | Scenario output log; current attach/detach. |
| 12 | **Write the mark-movement attribution**: for each priced tranche, current vs. prior clean price / DM / writedown with a one-line "vs. prior, because" decomposition across rates / spread / paydown / credit (PD-LGD) / methodology / date. **Do not finalise a move you cannot explain.** | manual | Mark-attribution record per tranche. → `../templates/mark-attribution.md` |
| 13 | **Confirm model checks**: `Inputs!D3` (total balance) and `D4` (current balance) must read `OK`; scan required output areas for formula errors; preserve methodology. | excel_vba | Check summary. **Failed checks are hard stops.** |
| 14 | **Leave the report generalised** — do not automate report prose, exhibits, correlation outputs, or client-facing packages in the pilot. | — | Record the manual report scope. → `report-lane.md` |
| 15 | **Assemble evidence + exceptions**; mark **ready for human review only**. | manual | Evidence log + exception log. → `evidence.md` |

## 6a. Reinvestment-period status (why it matters)

Amortisation does not begin until the reinvestment/replenishment period ends (`Inputs!D17`,
`Replenishment_End_Date`). Before trusting amortised balances, record whether the deal is **in** the
period (static-ish pool, substitutions allowed, balances broadly held) or **past** it (amortising). A
pool that should still be revolving but shows amortisation — or vice versa — is a mismatch to escalate,
not to smooth.

## 7a. Realised vs defaulted/non-liquidated (why `H11` is its own step)

The DCF carries **three distinct loss states**, and the update must not conflate them: **future-expected**
loss on the performing pool (CDR × `H10` over the maturity profile), **realised** loss that has crystallised
(`L4`, severity `H10`, fixed), and **defaulted-but-not-yet-liquidated** loss (the whole defaulted/non-liquidated
EAD on the tab × `H11`, timed by `H12`). The `H11` path is **market-implied and re-marked
each period** — it moves as comparable-bond prices, Debtwire news, and recovery clarity change — whereas
`L4` does not move once finally determined. When a name liquidates, it leaves the tab for the realised line;
the estimate must **not** overwrite the crystallised figure. Full method and grounding (rating-agency
trading-price vs ultimate recovery; restructuring as a default): `defaulted-and-nonliquidated-borrowers.md`.

## 8a. The loss path (where SES sits)

The model turns PD/CDR × LGD/severity into projected losses, which the waterfall allocates to tranches
from the bottom up. **If the deal carries SES, the netting happens between "losses realised" and
"losses allocated to the tranche."** SES is not an `Inputs` cell — confirm it is reflected in the
waterfall/`Notes` logic (see `ses.md`). Getting this wrong overstates junior-tranche losses and the
writedown (`H34`).

## Quality gate before "ready for review"

A run is not done until: model checks pass (`D3`/`D4` = OK); every moved tranche mark carries a
vs-prior sentence; each source input has an evidence record; any missing/ambiguous field is logged as
an exception with a named owner; and the deliverable is explicitly marked **for human review, not
delivery**. If any of these is missing, the work is unfinished — that is the signal to dig.
