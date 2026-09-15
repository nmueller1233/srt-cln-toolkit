# Expected handling — registry granularity varies across clients / periods

Reference registries do not arrive in one shape. The same deal may be obligor-level one period and
pre-bucketed the next; one trustee ships rating + industry + maturity per name, another ships a sparse
summary. The canonical-tape adapter (`normalize_tape.py`) is the contract that must absorb that variation.

A correct run should:

1. **Tie out notional regardless of granularity.** Whether the registry is obligor-level line items or
   pre-bucketed summary rows, `SUM(rona)` must reconcile to the stated reference notional. A granularity
   change between periods is **not** an excuse for a tie-out break.
2. **Derive composition metrics only from fields the registry actually carries.** A CCC-concentration or
   single-industry test (see `composition-trigger`) needs a **rating** / **industry** column. If the
   registry omits it, the metric degrades to `NA` — it is **not** guessed. A composition trigger that
   cannot be evaluated is a **STOP for a missing input**, not a "pass."
3. **STOP on a missing *required* field rather than emit a blank.** A sparse registry missing maturity (or
   any field in `required_fields`), or a renamed column the mapping can't find, is a hard stop — the
   adapter exits non-zero and names the gap. Never fabricate.
4. **Adapt by mapping, not by code.** A new client's layout is a new issuer-mapping JSON
   (`adapters/issuer-mapping.template.json`), not a one-off transform — so the same guarantees hold for
   the next client and the next period.

Regression coverage: `tests/srt/test_registry_granularity.py`. **Guidance** — confirm per-deal required
fields and tie-out tolerance with your reviewer.
