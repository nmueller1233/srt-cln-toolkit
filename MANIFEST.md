# Package contents

The SRT / CLN toolkit combines eight workflow skills with reference material, Python helpers, synthetic examples and tests. Start with [README.md](README.md) and [INSTALL.md](INSTALL.md).

| Location | Contents |
|---|---|
| `skills/` | Router and seven specialist workflow lanes. |
| `scripts/` | Tape normalization, exposure-weighted inputs, CLN aggregation, shadow comparison and test runners. |
| `assets/srt/references/` | Process, workbook cell map, calculation conventions and source guidance. |
| `assets/srt/adapters/` | Canonical registry schema and example mappings. |
| `assets/srt/sandbox-scenarios/` | Synthetic worked cases and expected behavior. |
| `assets/srt/templates/` | Run state, evidence, exception and attribution records. |
| `assets/srt/source-snapshot.zip` | Compact reference snapshot used by the package consistency checks. |
| `tests/srt/` | Deterministic behavior, mapping, routing and package tests. |
| `evals/` | Synthetic workflow prompts and expected behaviors. |
| `docs/` | Architecture, commands, configuration and sources. |

Supply `Srt dcf.xlsm` and `cln.xlsx` separately, with the data and vendor access required for the intended run. Configure their local paths in `assets/srt/corpus.map.json`. The repository includes synthetic inputs; permissions for any additional data are specific to the run. See [DATA-REDACTION.md](DATA-REDACTION.md) and [LICENSE](LICENSE).

[TESTING.md](TESTING.md) describes the checks and their environments. The Python scripts and workflow skills retain the toolkit's existing calculation rules.
