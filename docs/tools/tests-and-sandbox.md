# Tests and synthetic scenarios

The automated checks exercise the Python helpers and selected workflow contracts. The synthetic scenarios also provide practice material for an analyst or an agent host. Run the helpers on the supplied files, compare the output with the applicable test or scenario notes, and retain your own run output.

## Run the suite

```console
python -m unittest discover -s tests/srt -t . -v
python scripts/run_integrity_check.py
```

Run from the repository root. The integrity runner also writes `coverage.xml`. [TESTING.md](../../TESTING.md) explains dependencies, workbook checks and skipped tests.

| Test modules | Main checks |
|---|---|
| `test_srt_scripts.py`, `test_adapter_fixes.py`, `test_registry_granularity.py` | Normalization, weighting, CLN buckets and stored calculation expectations. |
| `test_normalize_stop_artifacts.py`, `test_stop_gate_confusion.py` | Configured stop conditions and output handling. |
| `test_shadow_run.py`, `test_property_invariants.py` | Shadow outputs, missing-input signals, weighted-average bounds and exposure conservation. |
| `test_srt_sandbox_scenarios.py`, `test_sandbox_bravo.py`, `test_srt_defaulted_workout.py`, `test_defaulted_severity_h11.py` | Synthetic cases covering credit-input availability, SES, triggers and defaulted recovery. |
| `test_cln_write_contract.py`, `test_model_map_against_workbook.py` | Locally supplied workbook structure and the CLN copy-writing contract. |
| `test_plugin_packaging.py`, `test_srt_plugin_completeness.py`, `test_reference_index_integrity.py`, `test_skill_redesign_contract.py` | Package contents, skills and reference structure. |

All modules are under [tests/srt/](../../tests/srt/). The CLN calculation expectations use the parameter tables mirrored in the script. Workbook-contract tests require the actual documented workbook structure; they do not calculate a market mark.

## Pick a scenario

| Scenario | Practice focus | Starting material |
|---|---|---|
| [alpha-rollforward](../../assets/srt/sandbox-scenarios/alpha-rollforward/) | Quarterly credit inputs and comparison with a prior mark. | Registry CSV, prior-period mark and expected notes; use the Alpha adapter example. |
| [bravo-ses](../../assets/srt/sandbox-scenarios/bravo-ses/) | EUR inputs, SES and a defaulted exposure. | Registry, mapping, terms and expected notes. |
| [charlie-newdeal](../../assets/srt/sandbox-scenarios/charlie-newdeal/) | Reading new-deal terms and calibration requirements. | Terms and expected notes. |
| [new-deal](../../assets/srt/sandbox-scenarios/new-deal/) | New-deal classification and calibration decisions. | Scenario JSON. |
| [delta-stop](../../assets/srt/sandbox-scenarios/delta-stop/) | Identifying source problems before model use. | Registry and expected notes. |
| [echo-defaulted-workout](../../assets/srt/sandbox-scenarios/echo-defaulted-workout/) | Defaulted and non-liquidated severity. | Registry, mapping, scenario and expected notes. |
| [lgd-only-registry](../../assets/srt/sandbox-scenarios/lgd-only-registry/) | Using supplied LGD while identifying missing forward PD. | Registry, mapping and scenario JSON. |
| [granularity-variation](../../assets/srt/sandbox-scenarios/granularity-variation/) | Different registry shapes and aggregation choices. | Expected notes. |
| [composition-trigger](../../assets/srt/sandbox-scenarios/composition-trigger/) | Portfolio-composition triggers. | Scenario and expected notes. |
| [sequential-trigger](../../assets/srt/sandbox-scenarios/sequential-trigger/) | Triggered sequential payments. | Scenario JSON. |
| [ses-hardcoded-default](../../assets/srt/sandbox-scenarios/ses-hardcoded-default/) | Recomputing SES and residual losses for a new default. | Scenario JSON. |
| [split-amortisation](../../assets/srt/sandbox-scenarios/split-amortisation/) | Split amortisation mechanics. | Scenario and expected notes. |

The [README quick start](../../README.md#quick-start) runs Alpha. For Bravo normalization:

```console
python scripts/srt-registry-inputs/normalize_tape.py --tape assets/srt/sandbox-scenarios/bravo-ses/reference-registry.csv --mapping assets/srt/sandbox-scenarios/bravo-ses/mapping.json --out bravo-canonical.csv --report bravo-normalize.json
```

Use each scenario's supplied mapping and terms. A scenario folder is practice material; its presence does not mean every instruction or expected note is executed by the automated suite.

## Check scenario responses

Write the responses to these four scenarios in a `sandbox-output` directory, using the exact filenames:

- `ses-hardcoded-default.md`
- `new-deal.md`
- `lgd-only-registry.md`
- `sequential-trigger.md`

Then run:

```console
python tests/srt/verify_sandbox_outputs.py sandbox-output
```

The checker examines the Markdown files present, identifies each scenario by its filename and tests required text patterns. It accepts a single Markdown path as well. It returns 0 when those files pass, 1 for missing patterns or unknown scenario names, and 2 when no Markdown files are found. To check all four cases, include all four files; it does not require absent cases automatically.

The checker evaluates response content through text matching. Independently compare calculations and transaction reasoning with the scenario and process references. It does not invoke an agent or calculate a valuation.
