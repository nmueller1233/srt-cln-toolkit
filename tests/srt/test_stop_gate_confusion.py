"""Confusion-matrix test over the SRT STOP/PROCEED mechanics.

Same logic as the triggering confusion matrix (TP/FP/FN/TN -> recall, specificity),
but applied to the DETERMINISTIC SRT decision gates instead of LLM skill-triggering --
so it ships in the plugin and runs with no CLI, no network, no client data.

Positive class = "the gate should STOP". Each labelled case runs a real mechanic
(`choose_path`, `internal_rating_check`, `aggregate`, or `pd_lgd_weighted_average`'s
exit code) and we record predicted-stop vs expected-stop. Because the mechanics are
deterministic, the matrix must be PERFECT: any FN (a real stop the gate missed -- the
dangerous quadrant) or FP (a valid run wrongly blocked) is a regression and fails.

Synthetic obligors only.
"""
import contextlib
import csv
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
for _cand in (PLUGIN_ROOT / "scripts" / "srt-registry-inputs", PLUGIN_ROOT / "scripts"):
    if (_cand / "aggregate_to_cln.py").exists():
        sys.path.insert(0, str(_cand))
        break
import aggregate_to_cln as agg          # noqa: E402
import pd_lgd_weighted_average as pld    # noqa: E402

LOAN_CFG = {"rona_col": "rona", "loan_type_col": "loan", "region_col": "region",
            "external_rating_cols": [], "bond_loan_flag": "Loan", "deal": "T"}
BOND_CFG = dict(LOAN_CFG, bond_loan_flag="Bond")


def confusion_matrix(results):
    """results: list of (predicted_stop: bool, expected_stop: bool). STOP = positive."""
    tp = sum(1 for p, e in results if p and e)
    fp = sum(1 for p, e in results if p and not e)
    fn = sum(1 for p, e in results if not p and e)
    tn = sum(1 for p, e in results if not p and not e)
    recall = tp / (tp + fn) if (tp + fn) else 1.0           # stops correctly caught
    specificity = tn / (tn + fp) if (tn + fp) else 1.0      # valid runs correctly passed
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "recall": recall, "specificity": specificity}


def _pd_lgd_stops(rows, header, extra_args=()):
    """Run pd_lgd_weighted_average on a temp CSV; predicted_stop = nonzero exit code."""
    fd = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="", encoding="utf-8")
    with fd:
        w = csv.DictWriter(fd, fieldnames=header)
        w.writeheader()
        w.writerows(rows)
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = pld.main([fd.name, *extra_args])
        return code != 0
    finally:
        os.unlink(fd.name)


# Each case: (name, predicted_stop, expected_stop). predicted_stop comes from a REAL mechanic.
def build_cases():
    PERF = ["obligor_id", "rona", "pd", "recovery", "status"]
    clean = [{"obligor_id": "ob1", "rona": "100", "pd": "0.02", "recovery": "0.40", "status": "Performing"},
             {"obligor_id": "ob2", "rona": "150", "pd": "0.03", "recovery": "0.35", "status": "Performing"}]
    missing_rec = [{"obligor_id": "ob1", "rona": "100", "pd": "0.02", "recovery": "0.40", "status": "Performing"},
                   {"obligor_id": "ob2", "rona": "150", "pd": "0.03", "recovery": "", "status": "Performing"}]
    # a defaulted / non-liquidated tab carries NO forward PD (the names have defaulted);
    # the H11 severity path keys off recovery, so the tab has no pd column.
    DEF = ["obligor_id", "rona", "recovery", "status"]
    defaulted = [{"obligor_id": "ob1", "rona": "60", "recovery": "0.40", "status": "Defaulted"},
                 {"obligor_id": "ob2", "rona": "40", "recovery": "0.30", "status": "Defaulted"}]

    cases = [
        # --- choose_path: methodology-consistency gate ---
        ("path: aggregate-calibrated, tape now has PD/LGD", agg.choose_path("aggregate", True, False)[1], True),
        ("path: obligor-calibrated, tape lost PD/LGD",       agg.choose_path("obligor", False, False)[1], True),
        ("path: unknown prior methodology",                  agg.choose_path("mystery", False, False)[1], True),
        ("path: new deal with obligor PD/LGD",               agg.choose_path(None, True, True)[1], False),
        ("path: obligor-calibrated, tape still has PD/LGD",  agg.choose_path("obligor", True, False)[1], False),
        ("path: aggregate-calibrated, tape still lacks it",  agg.choose_path("aggregate", False, False)[1], False),
        # --- internal_rating_check ---
        ("rating: internal-only, no external mapping",       agg.internal_rating_check(True, False)[0], True),
        ("rating: internal-only WITH mapping",               agg.internal_rating_check(True, True)[0], False),
        ("rating: external ratings present",                 agg.internal_rating_check(False, False)[0], False),
        # --- aggregate(): severity computability ---
        ("aggregate: Bond table, weight on a no-recovery loan type",
         bool(agg.aggregate([{"rona": "100", "loan": "Revolver"}], BOND_CFG)["stops"]), True),
        ("aggregate: Loan table, normal pool",
         bool(agg.aggregate([{"rona": "100", "loan": "Term Loan"}], LOAN_CFG)["stops"]), False),
        # --- pd_lgd exit codes ---
        ("pd_lgd: defaulted-only tab, no --include-defaulted", _pd_lgd_stops(defaulted, DEF), True),
        ("pd_lgd: required recovery missing on a row",          _pd_lgd_stops(missing_rec, PERF), True),
        ("pd_lgd: clean performing obligor tape",               _pd_lgd_stops(clean, PERF), False),
        ("pd_lgd: defaulted-only tab WITH --include-defaulted (H11)",
         _pd_lgd_stops(defaulted, DEF, ("--include-defaulted",)), False),
    ]
    return cases


class StopGateConfusionTests(unittest.TestCase):
    def setUp(self):
        self.cases = build_cases()
        self.cm = confusion_matrix([(p, e) for _, p, e in self.cases])

    def test_no_missed_stops_or_false_alarms(self):
        """Deterministic mechanics -> a perfect matrix. FN = a real STOP the gate missed
        (the dangerous quadrant); FP = a valid run wrongly blocked."""
        missed = [name for name, p, e in self.cases if e and not p]   # FN
        false_alarms = [name for name, p, e in self.cases if p and not e]  # FP
        self.assertEqual(missed, [], f"gate MISSED stops (false negatives): {missed}")
        self.assertEqual(false_alarms, [], f"gate over-stopped (false positives): {false_alarms}")
        self.assertEqual(self.cm["recall"], 1.0)
        self.assertEqual(self.cm["specificity"], 1.0)

    def test_matrix_is_non_vacuous(self):
        """Both classes must be exercised, or a 'perfect' matrix would be meaningless."""
        self.assertGreater(self.cm["tp"], 0, "no STOP cases exercised")
        self.assertGreater(self.cm["tn"], 0, "no PROCEED cases exercised")
        self.assertEqual(self.cm["tp"] + self.cm["fp"] + self.cm["fn"] + self.cm["tn"], len(self.cases))


if __name__ == "__main__":
    cm = confusion_matrix([(p, e) for _, p, e in build_cases()])
    print(f"STOP-gate confusion matrix: {cm}")
    unittest.main()
