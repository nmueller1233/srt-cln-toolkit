# AGENTS.md — SRT / CLN quarterly-update plugin (`structured-credit-automation`)

## Where things live (shared with Claude Code via `CLAUDE.md` → `@AGENTS.md`)
- **Where things live:** router `skills/srt-quarterly-update/SKILL.md` · lane skills `skills/srt-*` · references `assets/srt/` (`reference-load-index.md`, `references/`, `corpus.map.json` = the ONLY host-specific file) · scripts `scripts/srt-registry-inputs/`, `scripts/srt-review-package/shadow_run.py` (read-only) · tests `tests/srt/` · evals `evals/` · redaction policy `DATA-REDACTION.md`.
- **How to test:** `python -m unittest discover -s tests/srt -t . -v` (see Testing below; count the skips).
- **Gate log:** none in-repo — the mark's evidence is the quarterly review package the `srt-review-package` lane produces, plus the "vs. prior, because" attribution.
- **Off-limits:** any write to `Srt dcf.xlsm` by code · methodology switches without a STOP · real client/deal names in deliverables, exports or git · answering CRE/CMBS/CLO/consumer-pool/debt-stack questions here.
- **Who reviews:** a human sets and reviews every mark; client-facing output needs recorded human approval (the model owner).

Operating rulebook for **running** the SRT/CLN quarterly fair-value update with this plugin.
`Srt dcf.xlsm` is the calculation **source of truth**; the plugin guides mapped-input updates and
review gates — it does not replace the model, rewrite formulas, or approve client-facing marks.
Self-sufficient for a portable deploy; where a project-level `AGENTS.md` is also present, inherit its
contract (intake-first, model-as-source-of-truth, no redesign without approval, auditable evidence,
human review).

## Start every run
1. Load `skills/srt-quarterly-update/SKILL.md` (the router) first.
2. Then open `assets/srt/reference-load-index.md` and load **one** primary reference for the lane —
   **do not bulk-load.** Lanes: calibration -> `srt-calibration`; legal/deal mechanics ->
   `srt-legal-deal-mechanics`; registry/tape -> `srt-registry-inputs`; quarterly model mechanics ->
   `srt-quarterly-model-update`; evidence/exceptions/attribution/review -> `srt-review-package`;
   conceptual/theory questions -> `srt-difficulties`; correlation / copula exhibit (report-only) -> `srt-copula`.
3. Collect intake before any model-touching work: deal / test-case; run type (quarterly update · new deal ·
   amendment · report · read-only shadow); period end; **data classification (live / redacted /
   synthetic)**; sources available; SES yes/no; reinvestment status; currency / reference rate; expected
   outputs; manual steps to keep manual. **Missing intake → stop and ask.**

## Environment — verify this first
`assets/srt/corpus.map.json` is the **only** environment-specific file. It maps `corpus_root`,
`model_skeleton.srt_dcf_model`, and `cln_performance_curve`. On any new host, confirm those paths resolve
to the real `Srt dcf.xlsm` + `cln.xlsx`. **If they don't, the workbook-bound tests SKIP silently** (a
misleadingly low pass count) and model-tied steps can't run — verify before trusting a run.

## What's automated (and what isn't)
Code automates only the deterministic, judgment-free prep and checks; the model stays human.
- **Automated (scripts under `scripts/srt-registry-inputs/`):** `normalize_tape.py` (raw tape → canonical
  registry), `pd_lgd_weighted_average.py` (RONA-weighted PD/LGD), `aggregate_to_cln.py` (CLN
  rating/loan/region bucketing + an **inputs-only** row saved with openpyxl into a *copy* of `cln.xlsx`: formulas
  kept, CapIQ connections and charts dropped; the script writes to the supplied path, so select the copy explicitly).
  `scripts/srt-review-package/shadow_run.py` reads the supplied inputs without changing the workbooks;
  its optional `--report` argument saves the diagnostic comparison as JSON.
- **Human, never touched by code:** every `Srt dcf.xlsm` cell — copy the workbook, set HARD inputs,
  Goal-Seek `L30`, refresh DFs, roll `Spread Analysis`, source `H11`, run scenarios, write attribution,
  review. `process.md`'s **Lane** column tags each step (manual / power_query / vendor_addin / excel_vba /
  python_runner).
- **The line:** code prepares inputs and checks marks; **it never writes `Srt dcf.xlsm`.** The model is the
  calculation source of truth and the audit artifact — a human-set, human-reviewed mark is the deliverable.
  The remaining model-side work is judgment (H11, DM embedding, benchmark, attribution), which is exactly
  what should not be automated.

## Non-negotiables (every lane)
- Copy the model first; edit only mapped **HARD** input cells. Never overwrite formulas, named ranges, or
  the `Collateral`/`Notes` engines.
- **Recovery is not LGD:** `LGD = 1 − recovery`. Weight by **RONA**, never equal-weight.
- **Net SES against losses BEFORE the tranche writedown** (a waterfall mechanic; SES has no input cell).
- **Calibrate once:** Origination DM `L30` and the multiplier base (`L32`) are set at new-deal setup and
  held fixed; the quarterly mark rolls only the benchmark change (`'Spread Analysis'!D8`) through the held
  base -> `L34 = L30 × L32` (a trade printing on the deal is the rare exception).
- **Defaulted / non-liquidated severity (`H11`) is an ESTIMATE:** contract / fixed recovery first, else
  Debtwire research + the secondary price of the most comparable bond, RONA-weighted across the
  defaulted/non-liquidated tab (its **EAD**); re-marked each period; **never overwrite a realised loss
  (`L4` / `H10`)** with it.
- **PD/LGD method** (obligor-level vs registry→CLN aggregation) follows **last quarter's** calibration;
  switching paths is a **STOP** (methodology-driven mark variance).
- State the **day-count basis (`D22`)** and the rate source. Correlation is **report-only** (the DCF price
  does not consume the Gaussian copula). `Inputs!D3`/`D4` checks must read `OK`.
- **No mark ships without a "vs. prior, because" attribution.** The deliverable is **ready for human
  review**, never auto-delivered; client-facing output needs recorded human approval.

## Hard stops vs. clean answers (be decisive)
The deal's **legal agreement is the pricing basis** — it outranks the model default and last quarter's method,
and is **embedded at calibration**. On a roll-forward, apply the embedded logic and explain it; re-open the legal
doc only on an anomaly (new default · an input driving an unusual price move · a DM that fails to embed the deal's
risk · sense-checking another's odd pricing · methodology disagreement). Shape every triggered answer with
`assets/srt/references/response-structures.md`:
- **Clean answer** (apply + explain): embedded legal terms, triggers bounded by the agreement, SES netting,
  amortization structure, model mechanics.
- **Ask for details** (don't guess, don't escalate): registry / PD-LGD gaps, a RONA tie-out that won't reconcile.
- **Optional second look** (factors + recommendation + "a colleague"): defaulted-severity-without-a-contract ·
  benchmark selection · how much of a spread change to embed in the DM.
- **Hard stop** (don't proceed): data permissions unclear · a required input that can't be obtained · an
  unevidenced vendor refresh · a methodology switch/misalignment · fabrication risk · output going client-ready
  without human approval.

## Data discipline
Synthetic / redacted data only unless permissions for the **specific** run are confirmed (local access ≠
work entitlement). **Real client/deal names must not enter the deliverable.**

## Testing
```
python -m unittest discover -s tests/srt -t . -v      # use PYTHONIOENCODING=utf-8 on Windows
```
Workbook-bound tests (model-map ×3, cln-write ×2) run only when `corpus.map.json` resolves the workbooks;
otherwise they `@skipUnless`-skip. The CLN golden rows (0.2527 / 0.5229) are hard-coded constants and
always run — they guard the mirror in `aggregate_to_cln.py`, not the live `cln.xlsx`. Eval-layer statistics
(triggering confusion matrix, usability CIs) are kept in the author's private evaluation workspace and are
not part of this repository.

## Not for
CRE/CMBS · CLO/CDO · consumer-pool · single-borrower debt-stack · generic loan/equity models —
those are other workflow families. **Decline and redirect — do not attempt the calculation, not even a
"brief" or "for context" answer.** A governed valuation tool that answers an unsanctioned structure is a
worse failure than declining; name the right resource and stop.
