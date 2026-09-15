# Canonical Registry Schema

The normalized form every SRT reference tape is mapped into, so the rest of the skill (PD/LGD,
maturity profile, tie-out, shadow runs) works the same regardless of which trustee produced the report.
A per-issuer mapping (`issuer-mapping.template.json`) describes how to get *from* a raw tape *to* this.

## Why a canonical form

Real trustee/investor reports differ by issuer — different tab names, column headers, units, and date
formats (`registry-structure.md`). Rather than teach every downstream step every trustee's layout, the
**adapter** normalizes once into this schema, and everything downstream reads only this.

## Deal-level header (one record per run)

| Field | Type | Required | Notes |
|---|---|---|---|
| `deal` | string | yes | Deal name/code |
| `period_end` | date (ISO `YYYY-MM-DD`) | yes | Valuation period end |
| `currency` | string | yes | Deal currency (drives SOFR vs EURIBOR) |
| `stated_reference_notional` | number | yes | The deal's stated reference notional — the **tie-out target** for `SUM(rona)` |
| `ses` | object | no | `{carries: bool, rate: decimal, basis: string, reserve_bf: number}` if known |

## Obligor rows (one record per reference entity)

| Canonical field | Type | Required | Convention |
|---|---|---|---|
| `obligor_id` | string | yes | Unique key (name or LEI); used to diff vs prior period |
| `obligor_name` | string | no | Display name |
| `country_domicile` | string | no | |
| `country_incorporation` | string | no | |
| `industry` | string | no | |
| `rating` | string | no | Raw rating as reported |
| `rating_bucket` | enum | derived | `IG / BB / B / CCC / NA` (from `rating` via the mapping's `bucket_map`) |
| `maturity_date` | date (ISO) | **yes** | Drives the maturity profile |
| `rona` | number | **yes** | Reference Entity Notional Amount — the exposure weight; base-currency notional |
| `pd` | decimal | no* | Probability of default (decimal; `0.012` = 1.2%) |
| `recovery` | decimal | no* | Recovery rate (decimal) |
| `lgd` | decimal | derived | `1 − recovery` if `recovery` present; else from a `lgd` source column |
| `seniority` | string | no | e.g. Senior Secured / Senior Unsecured / Subordinated |
| `secured` | bool | derived | From `seniority` if not given |
| `status` | enum | no | `Performing / Defaulted` (default `Performing`) |
| `source_row` | int | auto | Row index in the raw tape (for audit) |

`*` `pd`/`recovery` may be partially or wholly absent — that is allowed. The adapter **does not fill
them**; missing values are reported so the loss engine uses the stratification fallback
(`pd-lgd-severity.md`) under recorded analyst judgment, never a silent default.

## Hard rules the adapter enforces (no-fabrication)

1. **Required fields** (`rona`, `maturity_date`, plus any in `required_fields`) must be present on every
   obligor row. A missing required field is a **stop**, not a guess.
2. **Tie-out:** `SUM(rona)` must reconcile to `stated_reference_notional` within `tie_out.tolerance_pct`.
   A gap beyond tolerance is a **stop**; if no stated notional is configured the tie-out is reported as
   **SKIPPED** (a loud note), never silently passed (the Delta scenario, automated).
3. **Range guard:** any `pd`/`recovery`/`lgd` outside `[0,1]` (or a negative `rona`) is a **stop** — it
   catches a percent/decimal mix-up or a bad cell rather than marking on garbage.
4. **Recovery → LGD** is the only credit derivation; the adapter never invents a PD or a recovery.
5. **Units are explicit, with a percent safety net** — the mapping states scales (`pd_scale`,
   `recovery_scale`, `rona_scale`); additionally any value written with a trailing `%` is divided by 100.
6. **Non-obligor rows are skipped** — totals/footer/blank rows (identity blank or in `non_obligor_labels`)
   are dropped, not ingested, so a report's "Total" line can't pollute the pool or trip a false stop.
7. **Mapped columns are validated** against the tape header — a missing mapped column is a **stop** if the
   field is required, else a loud note (this surfaces a renamed/moved column period-over-period).
8. **`obligor_id` is made unique** — a repeated identity (a multi-facility obligor) is disambiguated with a
   `#n` suffix so keyed period-over-period diffs don't collapse two lines. Map a facility/ISIN column to
   `obligor_id` when one exists.

Output: a `canonical-registry.csv` (these columns, in order) plus a `normalize-report.json` (rows in/out,
tie-out result, and any per-row problems). Exit code is non-zero if any hard rule fails.
