# Running the checks

Run the suite from the repository root with Python 3.11 or later:

```console
python -m unittest discover -s tests/srt -t . -v
```

Most checks use bundled synthetic inputs. Workbook-dependent checks require `openpyxl` and the local paths in [corpus.map.json](assets/srt/corpus.map.json). Read the test output for the current pass, failure and skip counts.

## Environment-aware runner

```console
python scripts/run_integrity_check.py
```

This runs the suite, prints the workbook and dependency checks, lists skips with their reasons, and writes `coverage.xml`. If both workbooks resolve and `openpyxl` is installed, every test must run: a skip causes exit code 1. On a host without those resources, skips are listed and allowed; test failures and errors still return exit code 1.

An exit code of 0 on a portable host therefore means that the checks which ran passed. Use the printed skip list to identify checks requiring another environment. The text-screening test also requires a locally supplied `SHOWCASE_FORBIDDEN_TERMS` value, with terms separated by `|`.

The separate coverage command is:

```console
python scripts/run_srt_tests_with_coverage.py
```

Coverage records executed Python lines. It does not measure financial accuracy or acceptance of a mark.

## What each check establishes

| Check | Evidence it provides |
|---|---|
| Tape normalization and weighting | Configured field checks, units, recovery-to-LGD conversion, exposure weighting and synthetic RONA reconciliations. |
| CLN aggregation | Bucket allocation, calculation against the script's stored parameter tables, and treatment of mapping exceptions. |
| STOP and artifact tests | Selected invalid inputs produce the expected stop signal and diagnostic artifacts. |
| Shadow calculation | Expected Alpha credit inputs and additive DM; missing-PD stops; explicit reporting when spread duration is absent. |
| Property tests | Weighted-average bounds and conservation of mapped plus unmapped exposure in the cases tested. |
| Model-map contract | Expected cell types, formula text and named ranges in a locally supplied SRT workbook. It reads the workbook without saving it. |
| CLN write contract | Input values and translated formulas in a temporary copy of the supplied CLN workbook, with existing rows checked. |
| Package and reference checks | Required files, skill structure and referenced documents. |

The CLN calculation tests use parameter constants stored in [aggregate_to_cln.py](scripts/srt-registry-inputs/aggregate_to_cln.py). They compare against those stored expectations; inspect the parameter table and mapping when the source CLN workbook changes. The model-map test also expects a particular formula base in `L32`, so interpret its result against the workbook contract described in [the cell map](assets/srt/references/model-cell-map.md).

## Scenario practice

The [sandbox guide](docs/tools/tests-and-sandbox.md) describes the supplied cases and the standalone checker for scenario notes:

```console
python tests/srt/verify_sandbox_outputs.py sandbox-output
```

Create `sandbox-output` with the Markdown scenario responses you want checked. The checker recognizes four scenario names and tests for required text patterns; it does not independently calculate the answer or invoke an agent.

## Using the results

Keep the test output with your environment record. For a valuation run, also retain the source reconciliation, model checks, scenarios and current-versus-prior attribution required by [the process](assets/srt/references/process.md). The automated checks support those records; the workbook calculates the mark and the model owner approves its use.
