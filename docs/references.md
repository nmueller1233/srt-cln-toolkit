# Sources and further reading

The package's [process](../assets/srt/references/process.md), [cell map](../assets/srt/references/model-cell-map.md) and transaction documents govern a run. The literature below provides financial and engineering background. A general reference does not establish a particular transaction's terms, a workbook calibration value or approval of a mark.

## Financial references

| Topic | Background sources retained from the toolkit bibliography | Package reference |
|---|---|---|
| Synthetic securitisation and risk transfer | European Banking Authority, *Guidelines on the determination of the weighted average maturity* and *Report on significant risk transfer* (2020); Basel Committee on Banking Supervision, *Basel III: revisions to the securitisation framework* (2016, 2018); Regulations (EU) 2017/2401 and 2021/557. | [SRT theory](../assets/srt/references/srt-theory-primer.md), [waterfall and triggers](../assets/srt/references/srt-waterfall-and-triggers.md) |
| CDS contracts, spread and settlement | ISDA, *2014 ISDA Credit Derivatives Definitions* and *Standard CDS Model* documentation; Dominic O'Kane, *Modelling Single-name and Multi-name Credit Derivatives*, Wiley, 2008. | [Common confusions](../assets/srt/references/common-confusions.md), [DM calibration](../assets/srt/references/spreads-dm-calibration.md) |
| Floating-rate valuation and discount margin | Frank J. Fabozzi (ed.), *The Handbook of Fixed Income Securities*, 9th ed., McGraw-Hill, 2021; Bruce Tuckman and Angel Serrat, *Fixed Income Securities*, 3rd ed., Wiley, 2011. | [Spreads and DM](../assets/srt/references/spreads-dm-calibration.md) |
| Credit benchmarks | S&P Global / IHS Markit, *CDX and iTraxx index rules*; ISDA, *Credit Derivatives Physical Settlement Matrix*. | [Benchmark spreads](../assets/srt/references/benchmark-spread-pulling.md) |
| Credit parameters and recovery | Basel Committee, *International Convergence of Capital Measurement and Capital Standards*, 2006; Edward Altman and Vellore Kishore, “Almost Everything You Wanted to Know About Recoveries on Defaulted Bonds,” *Financial Analysts Journal* 52(6), 1996. | [Credit parameters](../assets/srt/references/credit-risk-parameter-theory.md), [defaulted borrowers](../assets/srt/references/defaulted-and-nonliquidated-borrowers.md) |
| CLN default and recovery assumptions | Moody's *Annual Default Study* and default and recovery research are attributed by the source workbook's `Parameters` tab. The script's numerical constants are the workbook-derived table documented in the package. | [CLN aggregation](../assets/srt/references/cln-aggregation.md), [script constants](../scripts/srt-registry-inputs/aggregate_to_cln.py) |
| Default correlation and copulas | David X. Li, “On Default Correlation: A Copula Function Approach,” *Journal of Fixed Income* 9(4), 2000; John Hull and Alan White, “Valuation of a CDO and an nth to Default CDS Without Monte Carlo Simulation,” *Journal of Derivatives* 12(2), 2004. | [Copula theory](../assets/srt/references/srt-copula-theory.md) |
| Synthetic excess spread | European Banking Authority, *Final draft RTS on synthetic excess spread* (2022), and the transaction's own documents. | [SES](../assets/srt/references/ses.md) |
| Dates, rates and day counts | ISDA, *2006 ISDA Definitions* and *2021 ISDA Interest Rate Derivatives Definitions*; Federal Reserve Bank of New York, SOFR materials; European Money Markets Institute, EURIBOR materials. | [Dates and rates](../assets/srt/references/dates-rates-daycount.md) |
| Fair value and valuation evidence | FASB ASC 820, *Fair Value Measurement*; IFRS 13; International Private Equity and Venture Capital Valuation Guidelines, 2022. | [Evidence](../assets/srt/references/evidence.md), [report guidance](../assets/srt/references/report-lane.md) |

These entries retain the bibliography's edition and date descriptions. Consult the source publication and the applicable current transaction or reporting requirements for your use. Workbook constants and illustrative formulas are documented as package conventions, rather than attributed to a textbook as universal rules.

## Engineering references

| Topic | Reading | Related package component |
|---|---|---|
| Tests specifying behavior | Kent Beck, *Test-Driven Development: By Example*, Addison-Wesley, 2002. | [Tests](../tests/srt/) |
| Reproducible checks and explicit test outcomes | Jez Humble and David Farley, *Continuous Delivery*, Addison-Wesley, 2010; Martin Fowler, “Eradicating Non-Determinism in Tests,” 2011. | [Integrity runner](../scripts/run_integrity_check.py) |
| Explicit errors and recoverable execution | Eric S. Raymond, *The Art of Unix Programming*, Addison-Wesley, 2003, Rule of Repair. | [Normalizer](../scripts/srt-registry-inputs/normalize_tape.py) |
| Configuration and separation of responsibilities | Martin Fowler, *Patterns of Enterprise Application Architecture*, Addison-Wesley, 2002. | [Adapters](../assets/srt/adapters/) |
| Agent instructions and focused context | Anthropic, *Building effective agents* (2024), and Claude Code skills/context documentation. | [Router](../skills/srt-quarterly-update/SKILL.md), [reference index](../assets/srt/reference-load-index.md) |
| Task-focused documentation | Daniele Procida, *Diátaxis*. | [Installation](../INSTALL.md), [architecture](architecture.md), [script guide](tools/scripts.md) |

## Operating documents

| Need | Document |
|---|---|
| Step order, calibration and quarterly procedure | [process.md](../assets/srt/references/process.md) |
| Input cells, formula cells and named ranges | [model-cell-map.md](../assets/srt/references/model-cell-map.md) |
| Registry fields and units | [canonical-registry-schema.md](../assets/srt/adapters/canonical-registry-schema.md) |
| Required inputs and conditions for proceeding | [stop-items.md](../assets/srt/references/stop-items.md) |
| How to explain a movement or judgment | [response-structures.md](../assets/srt/references/response-structures.md), [mark-attribution template](../assets/srt/templates/mark-attribution.md) |

Retain each run's specific source documents and dates in its evidence log. Use the package [license](../LICENSE) and [data-redaction policy](../DATA-REDACTION.md) when sharing material.
