# SRT / CLN toolkit

Prepare reference-portfolio inputs, follow the quarterly valuation procedure, and explain changes in an SRT credit-linked note's mark. The toolkit combines eight workflow skills, Python helpers, model-input references, synthetic examples and a test suite.

The analyst calculates and reviews the mark in `Srt dcf.xlsm`. This repository supplies the procedure and supporting calculations; the workbook and `cln.xlsx` are supplied separately. The Python helpers normalize tapes, calculate exposure-weighted credit inputs, prepare CLN distributions and produce a shadow comparison. Every SRT model input is entered by the analyst.

## Quick start

From the repository root, use Python 3.11 or later. These commands use the bundled synthetic Alpha registry and require neither Excel nor a vendor connection.

```console
python scripts/srt-registry-inputs/normalize_tape.py --tape assets/srt/sandbox-scenarios/alpha-rollforward/reference-registry.csv --mapping assets/srt/adapters/issuer-mapping.example.json --out alpha-canonical.csv --report alpha-normalize.json
python scripts/srt-registry-inputs/pd_lgd_weighted_average.py alpha-canonical.csv
python scripts/srt-review-package/shadow_run.py --registry alpha-canonical.csv --input assets/srt/adapters/shadow-input.example.json --stated-notional 1000 --report alpha-shadow.json
```

The first command writes a canonical CSV and a normalization report. The second prints RONA-weighted PD and LGD, where RONA is the Reference Entity Notional Amount. The third writes a JSON comparison with the recorded example mark. Inspect the normalization report's `stops` and the shadow report's `would_stop` fields before using the results.

The Alpha example's expected values are RONA **1,000**, weighted PD **2.39425%**, weighted LGD **59.695%** and a shadow DM of **541 bps**. These values are asserted in [the Alpha self-test](tests/srt/test_shadow_run.py). They describe the bundled example.

Run the tests with:

```console
python -m unittest discover -s tests/srt -t . -v
```

See [installation](INSTALL.md) for Python, host and workbook setup, and [testing](TESTING.md) for required environments and how to interpret skips.

## Use the workflow

Load [the SRT router](skills/srt-quarterly-update/SKILL.md) in a host that can read Markdown skills. For example:

> Help me run an SRT quarterly update using synthetic data. The period end is 2026-06-30. Start with the reference registry, retain the prior period's credit methodology, and prepare the evidence and mark-attribution records. Workbook entries remain manual.

The router selects the relevant lane and collects the remaining run inputs: transaction or test-case identifier, run type, period end, data classification, available sources, SES status, reinvestment status, currency, reference rate and expected outputs. It loads one primary reference from the [reference index](assets/srt/reference-load-index.md).

The [fifteen-step process](assets/srt/references/process.md) governs the sequence:

| Steps | Work |
|---|---|
| 1–3 | Confirm context, copy the model for the period, and classify the run. |
| 4–5 | For a new deal or amendment, map legal terms; for a new deal, perform the prescribed calibration. Routine quarterly updates skip these steps. |
| 6–7 | Update the maturity profile and credit inputs using the established methodology; source defaulted and non-liquidated severity separately. |
| 8–10 | Confirm SES treatment, refresh discount factors and the fixing, then roll the benchmark spread inputs. |
| 11–13 | Calculate current attachment and detachment, run scenarios, explain mark movements, and check the model. |
| 14–15 | Keep report preparation manual and generalised; assemble evidence and exceptions for the model owner's review. |

For a new-deal par solve, record the collateral, loss, SES and discount-factor inputs already present in the copied model. Follow the process's calibration instructions if those inputs change later. Retain its stated order and document the reason for any re-solve.

## Inputs and outputs

| Starting material | Toolkit output | Analyst action |
|---|---|---|
| Raw CSV or XLSX tape and issuer mapping | Canonical registry, RONA reconciliation and exceptions | Confirm units, required fields, status and the stated notional. |
| Registry with PD and recovery or LGD | RONA-weighted credit inputs | Apply the method established at calibration and retained in the prior-period evidence. |
| Registry and CLN column mapping | Rating, loan-type and region distributions; CDR and severity self-checks | Check population and unmapped exposure before carrying inputs to the CLN workbook. |
| Canonical registry, prior mark and current market assumptions | Shadow estimate, movement bridge and comparison with a recorded mark | Compare the estimate with the workbook result and explain differences. |
| Current model, source records and prior-period evidence | Evidence log, exception log and mark attribution | Review each tranche and record model-owner approval before client use. |

The shadow calculation uses `prior DM + benchmark change / dampening divisor`. The workbook follows its documented multiplier formula, `L34 = L30 × L32`. Use the shadow result as an approximate comparison; take the valuation DM and clean price from the workbook. [Script guidance](docs/tools/scripts.md) explains the assumptions and outputs.

## Working with the Excel files

Supply the workbooks locally through [corpus.map.json](assets/srt/corpus.map.json). Read the [cell map](assets/srt/references/model-cell-map.md) before entering inputs. Preserve the model's formulas, named ranges and cash-flow engines. The workflow requires current source data, evidence of vendor refreshes, `Inputs!D3` and `D4` reading `OK`, and a current-versus-prior explanation for every moved mark.

The optional CLN writer updates an inputs row in a **copy** of `cln.xlsx`. Its openpyxl save preserves formulas but does not retain add-in connections or charts. Select the copy explicitly; the script does not distinguish it from the working original. No script writes `Srt dcf.xlsm`.

## Explore the package

| Guide | What it covers |
|---|---|
| [Architecture](docs/architecture.md) | How the router, references, scripts, workbooks and evidence fit together. |
| [Scripts](docs/tools/scripts.md) | Commands, mapping fields, output interpretation and calculation assumptions. |
| [Skills](docs/tools/skills.md) | Which lane to use and examples of requests. |
| [Tests and scenarios](docs/tools/tests-and-sandbox.md) | Automated checks and synthetic practice cases. |
| [Reference guide](docs/tools/references-corpus.md) | Where to find the process, cell conventions and financial explanations. |
| [Sources](docs/references.md) | Method documents and further reading. |

Use synthetic or redacted data unless the specific run is entitled to use live inputs. Keep client identities and local configuration out of shared files; see [DATA-REDACTION.md](DATA-REDACTION.md). Repository use is governed by [LICENSE](LICENSE). The plugin manifest uses the name `structured-credit-automation` for this toolkit.
