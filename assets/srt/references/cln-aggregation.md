# Registry → CLN Performance-Curve Aggregation

> **GUIDANCE — process + general credit theory.** Describes how a reference registry is turned into the
> `cln.xlsx` performance-curve inputs and how PD/LGD methodology is kept consistent across quarters. The
> **binding** numbers are the `cln.xlsx` `Parameters` tab and the deal documents; this file does not
> override them. The bucket constants below are **mirrored from the live `cln.xlsx`** — confirm against the
> file, and confirm any deal-specific treatment **with a colleague**, before a live mark.

## What the CLN file consumes

`cln.xlsx` → **`Performance Curves`** tab, **one row per deal**. The row holds RONA-weighted **distribution
inputs**; the file computes CDR and Severity itself from the `Parameters` reference tables. Helper:
`scripts/srt-registry-inputs/aggregate_to_cln.py`. Regression: `tests/srt/test_registry_granularity.py`.

| Cols | Input (we fill) | Buckets / order |
|---|---|---|
| `C` | Bond / Loan / Trade Finance | **per-deal single classification** (drives which rate table is used) |
| `D:H` | Rating distribution | **IG · BB · B · CCC · NA** |
| `I` | Include NA | **"Yes"** (protocol: NA kept as its own bucket) |
| `O:U` | Loan-type distribution | **Leverage Loan · Sn Unsecured · Sn Secured · Term Loans · Revolver · Trade Finance · Property** |
| `V:Z` | Geography distribution | **US · Eur · Middle East · India · EM/Asia** |
| `AA` | CPR | analyst input (default 0) |

**Computed by the file — never write these:** `J:N` (renormalized rating dist), `AB` **CDR**, `AC`
**Severity**. Write **inputs only, preserve every formula**, and **append a new row** for a deal/period not
yet present.

### The file's formulas (verified against the live named ranges)

- **Severity** `AC = 1 − SUMPRODUCT(O:U loan dist, avgRecovery[C]) / 100`
- **CDR** `AB = MAX(minCDR, SUMPRODUCT(J:N rating dist, avgCDR[C]) × SUMPRODUCT(V:Z geo dist, geoMult) / 100)`
- `minCDR = 0.0025`; `avgCDR`/`avgRecovery` selected by the `C` flag (Loan vs Bond vs Trade Finance).

The Python replica in `aggregate_to_cln.py` reproduces the live rows exactly (two live rows: 0.2527 and 0.5229)
and exists only to **self-check** the file and anchor the tests — the workbook stays source of truth.

> **⚠️ Known file quirk to flag, not silently fix.** `geographicCDRMult` resolves to
> `Parameters!AG4:AK4`, whose labels are **US, Eur, Latam, EM&FM, Asia**, but it multiplies the
> `Performance Curves` `V:Z` columns labelled **US, Eur, Middle East, India, EM/Asia** — **positionally**.
> So today Middle East × 0.473, India × 0.555, EM/Asia × 0.673. The labels and multipliers do not line up.
> Fill `V:Z` by the `Performance Curves` labels and **preserve the positional math**, but **flag this for
> human review** — do not re-wire it on your own.

## Writing the row (`aggregate_to_cln.write_cln_row`)

The helper writes the computed distribution into `cln.xlsx` **inputs-only, preserving every formula**.
Use it on a **copy** of the file (the run's period folder), never the live workbook.

```
python scripts/srt-registry-inputs/aggregate_to_cln.py \
  --registry <canonical-or-raw-registry.csv> \
  --config   <cln-mapping.json> \
  --cln      <period_folder>/cln-copy.xlsx   # a COPY of cln.xlsx
  [--cpr 0]
```

Behaviour and guarantees:
- **Update vs. append.** If the deal already has a row (matched on the Deal Name column), its inputs are
  updated in place; otherwise a **new row is appended below all existing content** (never inserted — an
  insert would not fix the file's formula references).
- **Inputs as values; formulas preserved.** It writes `C, D:H, I, O:U, V:Z, AA` as values (the full
  distributions sum to 1 only when every row maps to a bucket; unmapped RONA is reported in the notes and
is not renormalised — see rule 4 below). On append it copies the always-formula cells **`J:N` (renorm),
  `AB` (CDR), `AC` (Severity)** from the last data row and **translates them to the new row**, so the file
  computes them on open. The file is inconsistent row-to-row about which of `H`/`R`/`V` are formulas vs
  values; writing the full distribution as values sidesteps that.
- **Hard guard.** It refuses to write `J/K/L/M/N/AB/AC` as literals — those are the file's outputs.
- **STOP-aware.** If the aggregation raised any STOP (e.g. unmappable internal ratings, or a methodology
  switch), the CLI **skips the write** rather than producing a row off a flagged input.
- **A spot-check row** (e.g. `D=SUM(...)`, `V=SUM(...)`) may sit just below the data tied to the prior
  last row; appends land below it. Re-point or re-run any such manual check against the new row.

Contract test: `tests/srt/test_cln_write_contract.py` (skippable; needs openpyxl + the live file).

## Normalisation rules (always, regardless of source columns/granularity)

The reading script must absorb changing columns, differing rated-by coverage, and changing granularity
(obligor-level one quarter, pre-bucketed the next) and **always** map to the fixed buckets above.

1. **Ratings → IG/BB/B/CCC (+NA).** Map any external scale (S&P / Moody's) to the four buckets; blank → NA.
2. **Multiple agency columns:** pick, **per obligor**, the rating from the **most-populated** agency
   column, falling back across columns so coverage is maximised. Record which source was used per name.
3. **Internal ratings:** map internal grades to external via a recorded **internal→external mapping**, then
   bucket. **If the only ratings are *generic* internal grades with no mapping to the underlying risk,
   STOP and help the analyst investigate** — a generic internal grade cannot be bucketed without
   misstating risk. Never guess a bucket.
4. **Loan type / geography** map by the same fixed-bucket discipline; surface any RONA that cannot be
   mapped rather than dropping it silently. **Unmapped RONA treatment:** it stays in
   the denominator and in no bucket, so the emitted distribution sums to less than 1 and the file's formulas
   do not renormalise — unmapped loan type is priced at 100 % severity (severity biased **up**), unmapped
   region carries a zero CDR multiplier (CDR biased **down**). `aggregate_to_cln.py` reports the shortfall
   and the sums as a note, not a STOP; extend the mapping or record a judgment before the row is written.
   The script retains this denominator treatment. Also, `aggregate()` does **not** filter on status: pass the performing
   rows if the deal's methodology excludes defaulted names from the forward CDR.
5. **NA is its own bucket** (`Include NA = "Yes"`); it carries the `NA*/All` blended default rate.

## The two PD/LGD paths — chosen by methodology consistency, not by the new tape

`aggregate_to_cln.choose_path()` enforces this. The deciding factor is **what the deal was calibrated on**,
because changing methodology mid-life injects a mark move that is *methodology-driven*, not risk-driven.

| Prior methodology | New tape has obligor PD/LGD? | Action |
|---|---|---|
| none (new deal) | no | **Aggregate.** Record aggregation as the calibrated method. |
| none (new deal) | yes | **Obligor path.** Record obligor-level as the calibrated method. |
| obligor | yes | **Continue obligor.** |
| obligor | no | **STOP** — don't silently fall back to aggregation; investigate the source gap; human review. |
| aggregate | no | **Continue aggregation.** |
| aggregate | yes | **STOP.** Two consistent paths: (a) keep aggregating to avoid a methodology-driven variance in the submitted mark, or (b) switch to obligor-level and **attribute the change to the methodology shift, not to risk.** Investigate divergence; **human review** before deciding. |

## Quarterly update: methodology first

Before touching PD/LGD on a quarterly update, **read last quarter's methodology for the same deal** (prior
run-state / evidence / mark-attribution). Stay **consistent** with it this quarter — **but do not replicate
a prior-quarter mistake**: if last quarter's approach was wrong, flag it, correct it deliberately, and
attribute the correction explicitly so the mark move is not mistaken for a risk change. (See `process.md`.)

## Sources (external grounding — not deal rules)

- Rating-bucket default rates and seniority-based recovery rates follow the standard agency framework:
  Moody's *Annual Default Study* / corporate default & recovery research; S&P Global Ratings *Default,
  Transition, and Recovery* studies. The specific constants used live in `cln.xlsx` `Parameters` (which
  cites Moody's default reporting).
- LGD = 1 − recovery, downturn/seniority recovery ordering: see `credit-risk-parameter-theory.md` and
  `pd-lgd-severity.md`. Methodology-consistency / no-unexplained-move discipline: `stop-items.md`,
  `../templates/mark-attribution.md`.
