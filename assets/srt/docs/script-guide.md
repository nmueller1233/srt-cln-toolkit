# scripts/ — execution helpers (NOT skill logic)

These are **optional, deterministic execution helpers**, kept deliberately separate from the skill's
reasoning. The skill's logic lives in `SKILL.md` + `references/`; nothing in the process *depends* on a
script. A host's Python lane (the `python_runner` lane in `process.md`), or the analyst locally, may run them to remove
repetitive arithmetic. They are **standard-library-only Python**, so they port to any host with no
install.

Design rules (keep them portable):
- No Claude/Codex API calls, no network, no third-party packages.
- Read inputs from a path/CSV and `corpus.map.json`; print results. No hidden state.
- **Refuse to fabricate.** If a required value is missing, exit non-zero with an escalation message —
  never silently fill (this mirrors the skill's hard stops).

## Helpers

### `pd_lgd_weighted_average.py`
RONA-weighted PD and LGD from a reference-registry CSV — the registry's own mechanic
(`WA LGD = 1 − SUMPRODUCT(recovery, RONA)/SUM(RONA)`). Excludes `Defaulted` rows by default, prints
`SUM(RONA)` for the analyst to tie out (the tie-out itself is `normalize_tape.py`), and stops on a missing
PD or recovery/LGD value on an included row. A registry with no PD column at all is the LGD-only / H11
path: it prints "WA PD: NOT COMPUTED" and does not stop.

```
python scripts/srt-registry-inputs/pd_lgd_weighted_average.py <registry.csv> [--include-defaulted]
```

### `normalize_tape.py`
Raw issuer/trustee tape → canonical registry, driven by a per-issuer mapping JSON. STOPs (exit 1) on a
missing required field (as listed in the mapping's `required_fields`), an impossible credit value, a
required column absent from the tape, or a RONA tie-out failure when a stated notional is configured. On a
STOP the rows go to `<out>.STOPPED.csv`, never to `<out>`.

```
python scripts/srt-registry-inputs/normalize_tape.py --tape RAW.csv --mapping issuer-mapping.json --out canonical.csv [--report report.json]
```

### `aggregate_to_cln.py`
Canonical registry → the CLN performance-curve distribution inputs (rating / loan type / region), with a
self-check of the file's CDR and severity formulas. Optional `--cln` writes an inputs-only row into a
**copy** of `cln.xlsx` (openpyxl preserves formulas but not add-in connections or charts). Does not filter
on status; reports unmapped RONA as a note.

```
python scripts/srt-registry-inputs/aggregate_to_cln.py --registry canonical.csv --config cln-mapping.json [--out result.json] [--cln COPY-of-cln.xlsx]
```

### `shadow_run.py` (`scripts/srt-review-package/`)
Read-only shadow check: canonical registry + prior mark + this period's market inputs → exact RONA-weighted
PD/LGD, tie-out and dampened DM, plus an approximate clean-price estimate and its agreement with the
recorded actual mark. Writes nothing but its own report.

```
python scripts/srt-review-package/shadow_run.py --registry canonical.csv --input shadow-input.json [--report shadow.json]
```
