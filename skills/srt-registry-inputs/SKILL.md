---
name: srt-registry-inputs
description: Use when SRT/CLN work involves trustee registry/tape readiness, RONA tie-out, ratings, PD/LGD/recovery, defaulted-obligor source data, canonical mapping, obligor weighted averages, or CLN performance-curve aggregation.
---

# SRT Registry Inputs

Prepare current-period registry/tape data before model use.

Load `core-contract.md`, then the load index.

Rules:

- Map by meaning, not exact column names.
- Tie `SUM(RONA)` to reported notional before use.
- Convert recovery to LGD and weight by RONA.
- Preserve the calibrated PD/LGD path; switching obligor-level and CLN
  aggregation methods is a STOP.
- Keep defaulted names in notional tie-out, exclude them from forward PD/LGD,
  and route H10/H11 treatment to `srt-quarterly-model-update`.

Scripts under `../../scripts/srt-registry-inputs/`:

| Script | Purpose |
|---|---|
| `normalize_tape.py` | canonical registry, mapping, rating buckets, recovery-to-LGD, RONA tie-out |
| `pd_lgd_weighted_average.py` | RONA-weighted WA PD / WA LGD |
| `aggregate_to_cln.py` | CLN bucketing and an inputs-only write into a *copy* of `cln.xlsx` (`--cln <path>`) |

Scripts prepare inputs and never touch `Srt dcf.xlsm`; use copies or
synthetic/redacted data unless live permission is confirmed.

References: `registry-structure.md`, `canonical-registry-schema.md`,
`adapter-guide.md`, `cln-aggregation.md`, `pd-lgd-severity.md`.
