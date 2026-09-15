# Reference guide

Use [reference-load-index.md](../../assets/srt/reference-load-index.md) to select the primary document for a question. Load that document first and add another when the task crosses topics. The references describe the existing SRT procedure and workbook conventions.

| Question | Start here | Supporting reference |
|---|---|---|
| What is the quarterly sequence? | [process.md](../../assets/srt/references/process.md) | [core-contract.md](../../assets/srt/references/core-contract.md) |
| Which cells are inputs, formulas or outputs? | [model-cell-map.md](../../assets/srt/references/model-cell-map.md) | [model-input-cheatsheet.md](../../assets/srt/references/model-input-cheatsheet.md) |
| What must the registry contain? | [registry-structure.md](../../assets/srt/references/registry-structure.md) | [canonical-registry-schema.md](../../assets/srt/adapters/canonical-registry-schema.md) |
| How are PD, recovery and LGD used? | [pd-lgd-severity.md](../../assets/srt/references/pd-lgd-severity.md) | [credit-risk-parameter-theory.md](../../assets/srt/references/credit-risk-parameter-theory.md) |
| How is defaulted and non-liquidated exposure treated? | [defaulted-and-nonliquidated-borrowers.md](../../assets/srt/references/defaulted-and-nonliquidated-borrowers.md) | [evidence.md](../../assets/srt/references/evidence.md) |
| How does the registry feed the CLN workbook? | [cln-aggregation.md](../../assets/srt/references/cln-aggregation.md) | [adapter-guide.md](../../assets/srt/adapters/adapter-guide.md) |
| How are origination and valuation-date DM handled? | [spreads-dm-calibration.md](../../assets/srt/references/spreads-dm-calibration.md) | [benchmark-spread-pulling.md](../../assets/srt/references/benchmark-spread-pulling.md) |
| What are the fixing, date and day-count conventions? | [dates-rates-daycount.md](../../assets/srt/references/dates-rates-daycount.md) | [model-cell-map.md](../../assets/srt/references/model-cell-map.md) |
| Where does SES enter the loss calculation? | [ses.md](../../assets/srt/references/ses.md) | [srt-waterfall-and-triggers.md](../../assets/srt/references/srt-waterfall-and-triggers.md) |
| Which legal terms must be mapped? | [legal-inputs.md](../../assets/srt/references/legal-inputs.md) | [model-input-cheatsheet.md](../../assets/srt/references/model-input-cheatsheet.md) |
| What evidence accompanies the mark? | [evidence.md](../../assets/srt/references/evidence.md) | [report-lane.md](../../assets/srt/references/report-lane.md) |
| How should an answer or exception be framed? | [response-structures.md](../../assets/srt/references/response-structures.md) | [stop-items.md](../../assets/srt/references/stop-items.md) |
| Where are the conceptual explanations? | [common-confusions.md](../../assets/srt/references/common-confusions.md) | [srt-theory-primer.md](../../assets/srt/references/srt-theory-primer.md), [glossary.md](../../assets/srt/references/glossary.md) |
| What does the correlation exhibit explain? | [srt-copula-theory.md](../../assets/srt/references/srt-copula-theory.md) | [srt-theory-primer.md](../../assets/srt/references/srt-theory-primer.md) |

## Read model examples in context

The cell map describes a particular workbook contract. Formula literals and stored CLN parameter tables are source-model conventions; confirm that the local workbook uses them before applying a mapped input. Preserve the origination calibration and prior-period method as the process directs.

The source process distinguishes performing-pool losses, realised losses and defaulted/non-liquidated estimates. Use its cell-specific instructions when reading `H10`, `H11`, `L4` and `L5`; resolve a transaction-specific interpretation with the model owner before changing an input.

The benchmark reference explains the existing workbook multiplier. The [script guide](scripts.md) separately describes the shadow script's additive approximation, so its output can be interpreted alongside the workbook.

## Supporting files

The [adapters](../../assets/srt/adapters/) contain the issuer mapping, CLN mapping and shadow-input examples. The [templates](../../assets/srt/templates/) contain records for each period. The [sandbox scenarios](tests-and-sandbox.md) provide practice material. Use the active files in these directories when operating the toolkit.

[Sources and further reading](../references.md) lists the background literature and the package documents that define its procedure.
