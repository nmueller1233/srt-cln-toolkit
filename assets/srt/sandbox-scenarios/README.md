# Mock Scenarios (synthetic, non-client)

Twelve synthetic scenarios: four narrative worked cases (below), five JSON cases (two run the scripts, three are
arithmetic keys that check their own stored figures), and
three documentation-only cases (`composition-trigger/`, `granularity-variation/`, `split-amortisation/` —
read by the evals, not asserted by tests). The data here is synthetic — invented obligors, deals and numbers
modelled on the real registry structure (`../references/registry-structure.md`) — with one exception: the alpha
scenario's origination margin (`prior-period-mark.md`, `shadow-input.example.json`) is the live model's
origination DM rounded to the basis point.

Each scenario folder holds the **inputs** an analyst would receive plus an **`expected-notes.md`** that
describes what a correct run produces — the reference a human (or a grader) checks the run against.

| Scenario | Folder | Exercises |
|---|---|---|
| **Alpha** — quarterly roll-forward, no SES | `alpha-rollforward/` | The core path: registry → RONA-weighted PD/LGD → DF/SOFR refresh → spread roll → scenarios → **vs-prior attribution**. |
| **Bravo** — SES-bearing deal | `bravo-ses/` | The **SES gate**: losses must net against the SES balance before tranche writedown. |
| **Charlie** — new-deal calibration | `charlie-newdeal/` | Map a CLN term sheet to cells, then **calibrate the Origination DM (L30) to par** at issuance. |
| **Delta** — missing-source / stop | `delta-stop/` | The run must **stop and escalate** (registry won't reconcile; refresh unverified), not guess. |

How to use them:
- As **documentation** — read a scenario to see the process end-to-end on a concrete case.
- As **tests** — give the scenario's inputs + the standard task prompt to a fresh agent and compare its
  output to `expected-notes.md`. (See `../../../evals/evals.json`.) Alpha, Bravo and Delta are also run
  through the real scripts by `tests/srt/test_shadow_run.py`, `tests/srt/test_sandbox_bravo.py` and
  `tests/srt/test_adapter_fixes.py` (`bravo-ses/mapping.json` is the issuer mapping that test uses).

These are deliberately small (10–14 obligors) so a weighted average is checkable by hand.

## JSON scenarios (`tests/srt/`) — grading keys, and which ones run code

These carry a `scenario.json` (inputs + an `expected` block). Be precise about what the tests prove:
`lgd-only-registry` and `echo-defaulted-workout` run the real scripts (`normalize_tape.py`,
`pd_lgd_weighted_average.py`); `ses-hardcoded-default`, `new-deal` and `sequential-trigger` are **grading
keys** — the test recomputes the scenario's own arithmetic and checks the stored `expected` flags, so no
toolkit code runs for them. The three documentation-only folders named above have no test at all; nor does the Charlie narrative
case, so four of the twelve are read by no test.

| Scenario | Folder | Exercises |
|---|---|---|
| SES hard-coded + new default | `ses-hardcoded-default/` | Loss nets against SES **before** tranche; a prior-quarter hard-coded SES must be recomputed. |
| New deal | `new-deal/` | New-deal **calibration**, not a roll-forward. |
| LGD-only registry | `lgd-only-registry/` | Registry gives LGD but no PD → **stop** on the missing required PD (runs `normalize_tape.py`). |
| Sequential trigger | `sequential-trigger/` | A trigger breach must switch the waterfall to sequential or **stop** for review. |
| **Echo — defaulted / non-liquidated + true-up** | `echo-defaulted-workout/` | Estimated severity (`H11`) → **SES netting** → equity/CE waterfall → **realised true-up** (`H10`). Proves the defaulted name is **excluded from forward-performing PD/LGD yet stays in the notional tie-out** (runs both scripts). See `../references/defaulted-and-nonliquidated-borrowers.md`. |

Run them all: `python -m unittest discover -s tests/srt -t . -p "test_*.py"`.
