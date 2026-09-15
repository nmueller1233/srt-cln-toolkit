# adapters/ — the L1 execution seam (tape → canonical → shadow)

This folder turns the skill from a *companion* (L0) into an *assisted execution agent* (L1) the moment
you have real tapes. It is the first, lowest-risk rung of the autonomy ladder: **read + compute only —
no model writes, no client delivery.** Everything here is platform-neutral and stdlib-first, so it ports
to Codex's Python lane unchanged.

## The two-step contract

```
raw trustee tape  --(issuer mapping)-->  canonical-registry.csv  --(prior mark + market)-->  shadow report
   (any issuer)        normalize_tape.py       (one schema)              shadow_run.py        (agreement)
```

1. **Normalize** (`scripts/srt-registry-inputs/normalize_tape.py`): map a heterogeneous trustee/issuer tape to the
   canonical schema (`canonical-registry-schema.md`) using a per-issuer mapping
   (`issuer-mapping.template.json`). One mapping per issuer; no code change for a new issuer.
   - Enforces the no-fabrication rules: required fields present, `SUM(rona)` ties to the stated notional
     within tolerance, recovery→LGD only. Stops (exit 1) otherwise — the Delta scenario, automated.
2. **Shadow-run** (`scripts/srt-review-package/shadow_run.py`): from the canonical registry + a prior mark + this
   period's market inputs (`shadow-input.example.json`), estimate the move and **diff it against the
   human's recorded actual mark**. Read-only measurement.

## Why shadow mode first

It is the safe way to earn trust before any write or delivery (autonomy ladder L-step 1):
- It runs on **last quarter's real tape**, where the human's mark already exists, so you can measure
  agreement (bp differences) and stop-correctness with **zero exposure** — no model is touched, nothing
  ships.
- The deterministic parts (RONA-weighted PD/LGD, the tie-out, the dampened DM roll, the stop decision)
  are exactly reproducible; the price *estimate* is transparent and clearly labelled as an estimate to
  be diffed, not a model output (the penny still comes from `Srt dcf.xlsm`).

## Files

| File | Role |
|---|---|
| `canonical-registry-schema.md` | The normalized schema everything downstream reads |
| `issuer-mapping.template.json` | Per-issuer mapping contract (copy + fill per trustee) |
| `issuer-mapping.example.json` | Worked mapping for the synthetic Alpha tape (self-test) |
| `shadow-input.example.json` | Prior mark + market inputs + recorded actual (self-test) |
| `scripts/srt-registry-inputs/normalize_tape.py` | Tape -> canonical (no-fabrication stops) |
| `scripts/srt-review-package/shadow_run.py` | Canonical + inputs -> agreement report (read-only) |

## Self-test (synthetic, runs today)

```
python scripts/srt-registry-inputs/normalize_tape.py \
    --tape assets/srt/sandbox-scenarios/alpha-rollforward/reference-registry.csv \
    --mapping assets/srt/adapters/issuer-mapping.example.json \
    --out /tmp/alpha-canonical.csv --report /tmp/alpha-normalize.json

python scripts/srt-review-package/shadow_run.py \
    --registry /tmp/alpha-canonical.csv \
    --input assets/srt/adapters/shadow-input.example.json
```

## When you have real access — the L1 → L2 path

1. **L1 (this folder):** write a mapping per live trustee; run normalize + shadow on the *prior* period
   for each deal; track mark agreement and stop precision/recall. No writes, no delivery.
2. **L2 (next):** add the Excel write lane (`scripts/`, VBA/xlwings/PAD) to key the canonical inputs into
   a *copy* of the model, read `H34`/`H36`, Goal-Seek `L30`, re-run `D3`/`D4`; keep the human gates at
   calibration, any stop, and delivery. See the project rulebook's automation-lane order and the Word
   guide ("How it can be developed").

Guardrails are unchanged from the skill: stops, no fabrication, model non-regression, evidence-by-
construction, human review before any client mark.
