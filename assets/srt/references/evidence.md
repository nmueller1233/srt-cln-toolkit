# Evidence & Exceptions

**Read for what every step must leave behind and where it lands in the control workbook.** The rule:
**every meaningful step leaves an evidence record.** A mark is not "done" because the number looks
right — it is done when each input is source-backed, each exception is owned, and the deliverable is
explicitly marked for human review.

## Three outputs of every run

1. **Run state** — the live checklist (`templates/run-state.json`), one entry per process step with
   status and lane. Mirrors the control workbook's **Pilot Run State** tab
   (`Step ID · Step Name · Lane · Status · Human Review · Notes`).
2. **Evidence log** — one row per source/action (`templates/evidence-log.csv`). Mirrors the **Evidence
   Log** tab: `Evidence ID · Description · Evidence Type · Path / Reference · Status · Required? · Owner
   · Notes`.
3. **Exception log** — one row per mismatch/stop/judgment (`templates/exception-log.csv`). Mirrors the
   **Exception Log** tab: `Exception ID · Description · Severity · Resolution Status · Impact / Notes ·
   Owner · Resolution Evidence`.

Keep the column names identical to the workbook tabs so a run's outputs paste straight in.

## Evidence each step must leave

| Step | Evidence record (minimum) |
|---|---|
| 1 Intake | Workflow, deal/test case, period end, target folder, **data classification**, expected outputs, manual steps; SES + reinvestment classification. |
| 2 Model copy | Source-model copy path. |
| 5 Calibration (new deal) | First-funding/issuance anchor; zero curve as-of that date; par solve of `L30`; calibrated DM vs. contractual margin with the gap explained. |
| 6 Portfolio | Registry path, tab/columns, **RONA tie-out to registry total**, reinvestment status. |
| 7 PD/LGD | Direct weighted average or fallback strata; recovery→LGD conversion; S&P snapshot (source/version/date) if used; override reason + reviewer. |
| 8 SES | SES yes/no; if yes — rate, reset/accrual basis, accumulated balance, losses netted, residual to tranche, legal/registry source. |
| 9 Rates/DF | Refresh export; before/after `DF_Dates`/`DF_DFs`; **day-count basis**; base-rate source URL + fixing date + value + currency/convention. |
| 10 Spread roll | Prior/current benchmark, CapIQ source, raw change, dampened adjustment + recorded rationale, before/after DM (or multiplier) bridge. |
| 11 Scenarios | Current attach/detach; price/DM/writedown scenario output log. |
| 12 Attribution | Per-tranche vs.-prior decomposition of price/DM/writedown across rates / spread / paydown / credit / methodology / date; explicit driver for any material move. |
| 13 Model QA | `Inputs!D3`/`D4` status; formula-error scan of required output areas. |
| 15 Assembly | Evidence log + exception log complete; deliverable marked **ready for human review only**. |

## Status vocabulary (match the workbook)

- Evidence `Status`: `Missing` → `Captured` → `Verified`. `Required?`: `Required` / `As needed`.
- Exception `Severity`: `Info` / `Warning` / `Blocker`. `Resolution Status`: `Open` / `Accepted` /
  `Resolved`.
- Run-state `Status`: `Not Started` / `In Progress` / `Blocked` / `Done`. `Human Review`: `Yes` / `No`.

## The "ready for review" gate

A run is ready only when: model checks pass (`D3`/`D4` = OK); every moved tranche mark carries a
vs-prior sentence; each source input has an evidence row; every exception has an owner and a resolution
status; and the deliverable is labelled **for human review, not delivery**. If any is missing, the run
is unfinished — dig, don't ship.
