@AGENTS.md

# Claude Code — structured-credit-automation (Claude-only lines)

`AGENTS.md` here is the plugin's full operating rulebook (it ships inside the plugin for Codex via
`.codex-plugin`); it is longer than the estate's 20-line convention on purpose and is canonical for
both harnesses. The estate block at its top answers the five where-things-live questions.

*(Author's environment — the adapters, skills and agents named below live in the author's Claude Code
estate and are not part of this repository.)*

- **In Claude Code the SRT corpus is reached through thin adapters** in `~/.claude/skills/srt-*`
  (router `srt-quarterly-update`; `srt-quarterly-model-update` is a routed sub-skill, not a trigger).
  Edit the skill bodies HERE (`skills/`), never in the adapters.
- Workbook touches (`Srt dcf.xlsm`, `cln.xlsx`) go through the `excel-lane` skill; the plugin's own
  rule stands — code never writes `Srt dcf.xlsm`.
- Tests: `PYTHONIOENCODING=utf-8 python -m unittest discover -s tests/srt -t . -v`; workbook-bound
  tests skip silently when `assets/srt/corpus.map.json` does not resolve — check the skip count.
- Deal documents (CDS confirmations, indentures) → `legal-doc-reader`; scanned pages → `page-extract`.
