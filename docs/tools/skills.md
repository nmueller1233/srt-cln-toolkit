# Skills and workflow requests

A skill is a Markdown procedure that an agent host reads when handling a matching task. Start with [srt-quarterly-update](../../skills/srt-quarterly-update/SKILL.md), the router. It chooses the task lane, difficulty and response style, then loads one primary reference through [the reference index](../../assets/srt/reference-load-index.md).

## Choose a task

| Skill | Use it for | Example request |
|---|---|---|
| [srt-quarterly-update](../../skills/srt-quarterly-update/SKILL.md) | Intake and routing for any SRT/CLN workflow. | “Help me run a quarterly SRT update. Start by identifying the inputs needed.” |
| [srt-calibration](../../skills/srt-calibration/SKILL.md) | New-deal setup, legal-to-model mapping, the origination DM par solve and multiplier-base derivation. | “Walk me through the new-deal calibration and the evidence to retain for L30.” |
| [srt-legal-deal-mechanics](../../skills/srt-legal-deal-mechanics/SKILL.md) | CDS confirmations, indentures, offering memoranda, SES, triggers and amortisation terms. | “Map the supplied synthetic terms to the model inputs and explain the SES loss order.” |
| [srt-registry-inputs](../../skills/srt-registry-inputs/SKILL.md) | Tape mapping, RONA reconciliation, credit inputs, defaulted-obligor sources and CLN distributions. | “Normalize the Alpha tape and show the exposure-weighted PD and LGD.” |
| [srt-quarterly-model-update](../../skills/srt-quarterly-model-update/SKILL.md) | The model steps of a quarterly roll, selected by the router. | “Guide the period update using the prior methodology and the mapped input cells.” |
| [srt-review-package](../../skills/srt-review-package/SKILL.md) | Source evidence, exceptions, mark attribution and shadow comparisons. | “Prepare the current-versus-prior explanation from these model results and source records.” |
| [srt-difficulties](../../skills/srt-difficulties/SKILL.md) | Conceptual questions about negative accrual, split amortisation, EAD, severity and CDS mechanics. | “Explain why defaulted-but-not-liquidated severity is updated separately.” |
| [srt-copula](../../skills/srt-copula/SKILL.md) | Default correlation and the Gaussian-copula report exhibit. | “Explain the correlation exhibit and which outputs it informs.” |

The copula lane supports explanation and reporting; the DCF price does not consume that exhibit. For CRE/CMBS, CLO/CDO, consumer-pool and generic corporate valuation work, use the corresponding workflow outside this toolkit.

## Start a period

Supply the transaction or synthetic case, run type, period end, data classification, available sources, SES status, reinvestment status, currency and reference rate, expected output, and any manual constraints. The host asks for missing intake before describing model entries.

For a routine quarterly update, retain the prior-period method and follow [the fifteen-step process](../../assets/srt/references/process.md), skipping its new-deal legal and calibration steps where directed. A legal amendment follows the legal lane. A new deal follows the calibration sequence and records the inputs present when the par solve is performed.

The analyst supplies legal interpretation, model entries, current defaulted-severity assumptions, benchmark judgment and mark approval. The scripts perform the specific file preparation and checks documented in [the script guide](scripts.md).

## Keep the record

Use the supplied [evidence log](../../assets/srt/templates/evidence-log.csv), [exception log](../../assets/srt/templates/exception-log.csv), [mark attribution](../../assets/srt/templates/mark-attribution.md) and [run state](../../assets/srt/templates/run-state.json). Record the source for each input, the established methodology, current-versus-prior changes and the model owner's decision.

The response instructions distinguish a practical procedure, an educational explanation and a judgment question requiring factors and a recommendation. The [response guide](../../assets/srt/references/response-structures.md) specifies the format; [stop items](../../assets/srt/references/stop-items.md) specify when required information or approval must be obtained before proceeding.

See [INSTALL.md](../../INSTALL.md) to load the skills in a host. The executable helpers can also be used directly from Python without an agent host.
