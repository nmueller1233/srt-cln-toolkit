# PD, LGD / Severity

**Read for step 7 — deriving the credit assumptions from the reference registry.** The model runs on a
**CDR/severity** loss engine, not on per-name PD directly, so the job is to turn obligor-level registry
data into the portfolio assumptions the model consumes (`H7` CDR scaling, `H10`/`H11` severity).

## Definitions (don't conflate)

- **PD** = probability of default. **LGD** = loss given default; the model labels this **severity**.
- **Recovery is not LGD.** If the registry gives a recovery rate, convert first: **`LGD = 1 − recovery`**.
- The model's **CDR** (constant default rate, `H7` scaling) is the flow assumption that the registry's
  weighted PD informs; the model's **severity** (`H10` liquidated, `H11` not-yet-liquidated) is the LGD.

## Where the numbers come from

The reference registry's **Reference Portfolio** tab (one row per obligor; `registry-structure.md`).
The exposure weight is **RONA** (Reference Entity Notional Amount).

## Step process

| Step | Process | Evidence / Control |
|---|---|---|
| 1. Inspect registry | Find obligor-level **PD**, **LGD/severity**, or **recovery** columns on the Reference Portfolio tab (and any pool-performance tab). **Column names vary — map by meaning, don't enforce strict names.** | Save the source workbook; note the actual tab/columns used. If mapping is ambiguous, **ask — don't guess.** |
| 2. Direct weighted average (if the fields exist) | `WA PD = SUMPRODUCT(PD, RONA)/SUM(RONA)`; `WA LGD = 1 − SUMPRODUCT(recovery, RONA)/SUM(RONA)` (convert recovery→LGD first). This is exactly how the registry computes it. *Calculation assumption:* both averages are exposure-weighted, so `CDR × H10` reproduces the pool's expected loss only if PD and LGD are uncorrelated across names; when weaker names also recover less, the product understates pool EL (≈ 3–7 % relative on the sandbox tapes). The toolkit retains the registry's exposure-weighted calculation. | Retain the calc range; **tie `SUM(RONA)` to the registry total.** |
| 3. Fallback stratification (if direct fields are absent) | Stratify the pool by rating, country/region, loan type, and secured/unsecured; enter the stratified figures and fill each required column from the strata. | Analyst-controlled input. Missing categories become notes/user inputs, **not** silent failures. |
| 4. Model-calculate from strata | Where direct PD/LGD is absent, derive PD and severity from the **current approved S&P Global default/recovery dataset** by rating, geography, and loan type. **Verify the dataset vintage each period — do not default to a prior year.** | Keep the S&P source/version/date in evidence; never hard-code stale values without an approved snapshot. |
| 5. User override allowed | Registry detail varies materially across deals; allow analyst judgment for incomplete ratings, mixed facility types, country groupings, or unusual exposure tags. | **Log the override reason and reviewer.** Do not smooth over missing data. |

## Stratification buckets (when you fall back)

| Dimension | Approved buckets | Note |
|---|---|---|
| Rating | IG, BB, B, CCC, NA | Use NA only when no defensible mapping exists. |
| Country / region | North America, Europe, Asia/EM, India, Middle East | Keep source country detail even when grouped. |
| Loan type | Revolver, term loan, leveraged loan, senior secured, senior unsecured | Labels overlap; analyst judgment expected. |
| Security status | Secured vs unsecured | Preserve the more detailed lien note if present. |
| Exposure weight | **RONA** | The weighting base unless the analyst approves another. |

## Where it lands in the model

The weighted PD informs the **CDR scaling (`H7`)**; the weighted LGD lands as **severity (`H10`**, with
`H11` for defaulted-not-liquidated). These are HARD inputs in the Collateral-Modelling block; the active
value used downstream is the `I`-column manual/scenario switch (`model-cell-map.md`). Recovery lag
(`H12`, periods) and payment lag (`H4`, days) are separate — don't conflate the units.

## Severity for the defaulted / non-liquidated bucket (`H11`) — different path

`H11` is **not** the performing-pool LGD above. It is the **RONA-weighted estimated severity** on names
that have **defaulted but not yet liquidated**, set by the **contract-first hierarchy** (full method +
grounding in `defaulted-and-nonliquidated-borrowers.md`):

1. **Contract first** — a contractual / fixed recovery if the deal specifies one (it governs the protection
   cashflow), **unless the client gives additional borrower-level insight**, which overrides.
2. **Else research** — per obligor, **Debtwire** material-change news (restructuring / distressed exchange,
   missed payment, bankruptcy) **+** the **secondary price of the most comparable bond** as a market-implied
   recovery (match seniority / lien / sector / tenor; price = recovery, severity = `1 − price`).
3. **RONA-weight across the defaulted/non-liquidated tab** → `H11 = 1 − WA recovery`
   (`scripts/srt-registry-inputs/pd_lgd_weighted_average.py --include-defaulted`, prices entered as a **fraction of par**).

`H11` applies to the **entire defaulted/non-liquidated EAD** on that tab (= outstanding notional / RONA for
funded exposures; `drawn + CCF×undrawn` for revolvers/undrawn — `credit-risk-parameter-theory.md`), is a
**market-implied estimate re-marked each period**, and is **distinct from realised loss** (`L4`, severity
`H10`, fixed). Recovery timing is `H12`. Once liquidation crystallises a name, it moves to the realised
line — **do not let the re-marked estimate overwrite it.**

## Gate and evidence

**Stop** if the PD/LGD direct fields or fallback strata are ambiguous and the analyst's judgment has not
been recorded — the process *allows* judgment, but unrecorded judgment is not evidence. Capture: the
registry path, the columns used, the recovery→LGD conversion, the RONA tie-out, the S&P snapshot if used,
and any override reason + reviewer.

For `H11`, additionally capture, per defaulted/non-liquidated name: the **contract clause** cited (or why
none applies) and any **client override**; the **Debtwire citations** (date / headline / source); the
**comparable bond(s)** used, their **secondary price + date**, and why they're comparable; and the
**RONA-weighting tied to the defaulted/non-liquidated tab total** (which should tie to `L5`). A reviewer
must be able to reproduce `H11` from these.
