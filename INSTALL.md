# Installation and first use

Keep the repository's directory structure intact. The skills refer to `assets/srt/` and `scripts/` by their package paths.

## Python setup

Use Python 3.11 or later. The CSV helpers and test runner use the standard library. Install `openpyxl` for XLSX tape reads, the optional CLN copy writer and workbook-dependent tests.

From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install openpyxl
$env:PYTHONIOENCODING = 'utf-8'
```

Activation is optional: use `.venv\Scripts\python.exe` in place of `python` if your shell does not permit activation. On other platforms, use the equivalent Python virtual environment command.

Start with the [synthetic quick start](README.md#quick-start). It writes `alpha-canonical.csv`, `alpha-normalize.json` and `alpha-shadow.json` in the current directory. No workbook paths are needed for this example.

## Load the workflow in an agent host

Open the repository as the working project and ask the host to read [AGENTS.md](AGENTS.md), then [skills/srt-quarterly-update/SKILL.md](skills/srt-quarterly-update/SKILL.md). This gives the host the operating instructions and the router. Confirm that it can resolve the reference and script paths before starting a period.

The package includes a [Codex plugin manifest](.codex-plugin/plugin.json), with the plugin name `structured-credit-automation` and `skills/` as its skill directory. Use your host's local-plugin installation mechanism if available. Loading the rulebook and router explicitly is sufficient to begin reading the workflow without relying on a host-specific registration command.

For Claude Code skill discovery, the skill folders can be copied into the project's `.claude/skills/` directory while `assets/` and `scripts/` remain at the project root. Keep the skill bodies synchronized with the package version. The repository also provides [CLAUDE.md](CLAUDE.md) as its rulebook entry point.

A first request is: **“Help me run an SRT workflow update.”** The host should identify the SRT lane and collect the run context before describing model changes. See [the skill guide](docs/tools/skills.md) for more specific prompts.

## Configure workbook access

For workbook work, supply your own `Srt dcf.xlsm` and `cln.xlsx`, Excel, and the approved data sources and add-ins required by your model. Edit [assets/srt/corpus.map.json](assets/srt/corpus.map.json) locally:

| Key | Set it to |
|---|---|
| `corpus_root` | The local directory containing your approved model and source files. |
| `model_skeleton.srt_dcf_model` | The SRT model path, relative to `corpus_root` or absolute. |
| `model_skeleton.cln_performance_curve` | The CLN workbook path, relative to `corpus_root` or absolute. |
| `run_io.period_folder_pattern` | Your per-period working directory pattern. |

The `process_docs`, `reference_examples` and `control_tower` entries point to optional local supporting material. Fill the entries used by your workflow. The included process, adapters and templates are available in `assets/srt/`. Keep the published configuration free of local paths and client identifiers.

Workbook paths are resolved as `corpus_root / model_skeleton.<key>`. Confirm that each resolves to the intended workbook. A missing workbook or missing `openpyxl` causes the relevant tests to skip.

The workbook contract tests expect the cell layout and formula text documented in the package, including the source model's `L32` base literal. Use them with that model contract. A different workbook requires a model-owner assessment of its mapping; a passed synthetic test cannot establish its compatibility.

## Configure a registry

Copy the [issuer-mapping template](assets/srt/adapters/issuer-mapping.template.json) into your period's working files. Set the source headers, date formats, numerical scales, default-status codes, required fields and stated reference notional from the supplied tape. The [Alpha mapping](assets/srt/adapters/issuer-mapping.example.json) is a runnable example; the [script guide](docs/tools/scripts.md) explains the fields.

For CLN aggregation, use a separate [CLN mapping](assets/srt/adapters/cln-mapping.example.json). Its rating, loan-type and geography columns must match the registry being passed to the aggregator. Record the prior-period methodology separately and follow the registry skill's path decision before running the helper.

## Verify the environment

```console
python -m unittest discover -s tests/srt -t . -v
python scripts/run_integrity_check.py
```

The second command also rewrites `coverage.xml` and lists every skipped test. When both workbooks resolve and `openpyxl` is installed, any skip makes that runner fail. The optional text-screening test requires `SHOWCASE_FORBIDDEN_TERMS`, a pipe-separated local list of terms to exclude; supply your actual screening terms when using that check.

Read [TESTING.md](TESTING.md) for the meaning of each result and the workbook checks' scope. Re-run the applicable checks after changing mappings, updating the package or replacing a workbook.
