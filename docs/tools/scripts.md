# Script guide

Run commands from the repository root with Python 3.11 or later. CSV preparation uses the standard library. XLSX tape reads and CLN workbook writes require `openpyxl`.

## Normalize a tape

[normalize_tape.py](../../scripts/srt-registry-inputs/normalize_tape.py) reads a tape and an issuer mapping, then writes a canonical registry and an optional JSON report.

```console
python scripts/srt-registry-inputs/normalize_tape.py --tape assets/srt/sandbox-scenarios/alpha-rollforward/reference-registry.csv --mapping assets/srt/adapters/issuer-mapping.example.json --out alpha-canonical.csv --report alpha-normalize.json
```

Use the [mapping template](../../assets/srt/adapters/issuer-mapping.template.json) for another source:

| Configuration | How to set it |
|---|---|
| `source.type`, `registry_sheet`, `header_row` | Select CSV or XLSX, the XLSX worksheet and the one-based header row. |
| `column_map` | Match canonical fields to exact source headers. Omit fields the source does not supply. |
| `transforms` | Set PD, recovery and RONA scales and accepted date formats. Decimal PD `0.012` means 1.2%; a numeric percent requires the appropriate scale. |
| `status_rules.defaulted_values` | List the source status codes identifying defaulted rows. |
| `required_fields` | Name fields required for this input route. The example requires RONA and maturity; it does not require PD. |
| `deal_meta.stated_reference_notional` | Supply a positive notional in the same units as normalized RONA to activate the reconciliation. A value of zero leaves that check skipped. |
| `tie_out` | Retain the approved defaulted-row inclusion rule and reconciliation tolerance. The supplied `tolerance_pct` is `0.005`. |

Read [the canonical schema](../../assets/srt/adapters/canonical-registry-schema.md) for field definitions. A value with a trailing `%` is also divided by 100; check the source representation before choosing scales. Recovery is converted to LGD as `1 − recovery`. Missing credit inputs remain missing.

The report records the input/output row counts, RONA reconciliation, notes and `stops`. A required-field or range failure, or a gap beyond the configured notional tolerance, returns exit code 1. On a stop, the CSV is written as `alpha-canonical.STOPPED.csv` rather than the normal output name. Use a new output path for each run so an earlier file cannot be mistaken for the current result.

## Calculate exposure-weighted PD and LGD

[pd_lgd_weighted_average.py](../../scripts/srt-registry-inputs/pd_lgd_weighted_average.py) reads a CSV and prints the selected columns, included and excluded rows, total RONA and weighted credit inputs.

```console
python scripts/srt-registry-inputs/pd_lgd_weighted_average.py alpha-canonical.csv
```

It calculates `Σ(PD × RONA) / ΣRONA`. LGD is `1 − weighted recovery`, with the LGD column used when a complete recovery calculation is unavailable. Rows whose status is `Defaulted` are excluded by default; `--include-defaulted` includes them for the separately specified population. The helper uses exposure weighting. Apply the existing model methodology when deciding how its output enters the workbook.

For the Alpha example, [test_shadow_run.py](../../tests/srt/test_shadow_run.py) asserts weighted PD `0.0239425` and weighted LGD `0.59695`. The printed percentages are rounded.

If a PD column is present but an included row lacks PD, the helper reports a stop. If the PD column is absent altogether, it reports **NOT COMPUTED** and may still return exit code 0 for an LGD-only calculation. Obtain required forward PD through the established input route before using the result in a forward-loss calculation. Normalize a raw tape first to apply its range and required-field checks.

## Prepare CLN distributions

[aggregate_to_cln.py](../../scripts/srt-registry-inputs/aggregate_to_cln.py) reads a CSV plus a separate [CLN mapping](../../assets/srt/adapters/cln-mapping.example.json). It prints JSON and can save it with `--out`.

```console
python scripts/srt-registry-inputs/aggregate_to_cln.py --registry period-registry.csv --config period-cln-mapping.json --out period-cln-inputs.json
```

Here `period-registry.csv` and `period-cln-mapping.json` are your prepared working files. Configure:

- `rona_col`, `loan_type_col` and `region_col` to match the actual CSV headers.
- `external_rating_cols` to name available agency-rating columns. The script prefers the most populated column and falls back across the others by row.
- `internal_rating_cols` and `internal_to_external_map` when an approved internal-grade mapping is used.
- `bond_loan_flag` to select the workbook's Loan, Bond or Trade Finance parameter table.

The returned JSON contains `rating_distribution`, `loan_type_distribution`, `region_distribution`, `rona_total`, `self_check_cdr`, `self_check_severity`, `cln_row_inputs`, `stops` and `notes`. Weights are fractions. The rating buckets retain `NA` explicitly.

Before running this command, apply the prior-period methodology decision in [the registry skill](../../skills/srt-registry-inputs/SKILL.md). The module defines `choose_path`, but its command-line entry point calls aggregation directly. It does not automatically enforce the prior-methodology decision or filter defaulted rows; provide the population required by the existing procedure.

Inspect all mapping notes before using the output. Unmapped loan-type weight remains in the denominator with zero recovery contribution, increasing the severity self-check. Unmapped geography has zero multiplier contribution, reducing the CDR self-check before its floor. These conditions produce notes rather than automatic stops. The geography multipliers follow the workbook's column positions even where the labels differ. The [CLN reference](../../assets/srt/references/cln-aggregation.md) describes the bucket order, fixed parameter tables and formulas.

### Optional workbook copy

Add `--cln cln-copy.xlsx` to write the distributions into a copy you have already created. The writer preserves the formula columns `J:N`, `AB` and `AC`; inputs occupy `C`, `D:H`, `I`, `O:U` and `V:Z`. `--cpr` supplies the row's CPR value and defaults to `0.0`; use the value required by the transaction's existing methodology.

The script skips the workbook write when `stops` is non-empty and returns exit code 1. Otherwise it saves the supplied path. **Use a copy:** this save does not retain CapIQ connections or charts, and the script does not refuse the working original. Open the copy in Excel to calculate its formulas before using the results.

## Compare a shadow estimate

[shadow_run.py](../../scripts/srt-review-package/shadow_run.py) reads a canonical registry and an [input JSON](../../assets/srt/adapters/shadow-input.example.json). It prints the estimate and can write a JSON report:

```console
python scripts/srt-review-package/shadow_run.py --registry alpha-canonical.csv --input assets/srt/adapters/shadow-input.example.json --stated-notional 1000 --report alpha-shadow.json
```

| Input block | Meaning and units |
|---|---|
| `prior` | Prior weighted PD/LGD and writedown as decimals, clean price in points, valuation DM in basis points. |
| `market` | Benchmark change in basis points, dampening divisor and spread duration. |
| `recorded_actual` | Optional current clean price, DM and writedown for comparison with the estimate. |
| `--stated-notional` or JSON `stated_reference_notional` | Optional RONA reconciliation target in the registry's units. |

The JSON example carries additional contextual fields. The current bridge does not calculate a rate effect from the SOFR fields.

The report contains `total_rona`, `perf_rona`, `estimate`, `agreement` and `would_stop`. The Alpha DM calculation is `545 + (-8 / 2) = 541` bps. The bridge scales prior writedown by the ratio of current to prior `WA PD × WA LGD`, uses spread duration for the spread-price effect and sets the rate contribution to zero.

Use the result as a comparison under these assumptions. Its additive DM calculation does not reproduce the workbook's multiplicative `L34 = L30 × L32`. The linear credit estimate does not implement tranche attachment/detachment caps or loss timing. The rate contribution does not measure the sensitivity of a discounted or heavily written-down tranche. When spread duration is missing, the output labels that contribution **not estimated** and omits it from the clean-price estimate.

The script writes no workbook. `--report` writes a diagnostic JSON file. A **WOULD STOP** result still returns exit code 0: inspect `would_stop`, warnings and the comparison fields, not just the process exit code.

## Test commands

[run_integrity_check.py](../../scripts/run_integrity_check.py) runs the suite with dependency checks and a named skip list. [run_srt_tests_with_coverage.py](../../scripts/run_srt_tests_with_coverage.py) supplies the trace-based coverage calculation. Both write `coverage.xml`. See [TESTING.md](../../TESTING.md) for commands and interpretation.
