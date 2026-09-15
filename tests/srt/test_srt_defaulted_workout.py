"""Deterministic regression for the echo-defaulted-workout sandbox scenario.

Covers the defaulted / non-liquidated -> estimated severity -> SES netting -> waterfall,
then the realised true-up path, AND proves (via the real scripts) the two principles:
a defaulted name is EXCLUDED from forward-performing PD/LGD yet STAYS in the notional tie-out.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCEN = PLUGIN_ROOT / "assets" / "srt" / "sandbox-scenarios" / "echo-defaulted-workout"
PY = sys.executable


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def load_script(name):
    path = PLUGIN_ROOT / "scripts" / "srt-registry-inputs" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ses_available(ses):
    accrual = ses["annual_rate"] * ses["performing_balance_mm"] * ses["quarter_fraction"]
    carry = 0.0 if ses["basis"] == "use_it_or_lose_it" else ses["brought_forward_balance_mm"]
    return accrual + carry


class EchoDefaultedWorkoutTests(unittest.TestCase):
    def setUp(self):
        self.s = load_json(SCEN / "scenario.json")

    def test_interim_estimated_severity_ses_netting_and_waterfall(self):
        s = self.s
        d = s["defaulted_obligation"]
        equity = s["capital_structure"]["equity"]["thickness_mm"]
        exp = s["expected"]["interim"]

        est_lgd = 1 - d["estimated_recovery"]
        gross = d["rona_mm"] * est_lgd
        ses = ses_available(s["ses"])
        residual = max(gross - ses, 0.0)
        equity_remaining = equity - min(residual, equity)
        mezz_writedown = max(residual - equity, 0.0)

        self.assertFalse(d["liquidated"])
        self.assertAlmostEqual(est_lgd, exp["estimated_lgd"], places=6)
        self.assertAlmostEqual(gross, exp["gross_estimated_loss_mm"], places=6)
        self.assertAlmostEqual(ses, exp["ses_available_mm"], places=6)
        self.assertAlmostEqual(residual, exp["residual_to_tranche_mm"], places=6)
        self.assertAlmostEqual(equity_remaining, exp["equity_remaining_mm"], places=6)
        self.assertAlmostEqual(mezz_writedown, exp["mezz_writedown_mm"], places=6)
        self.assertTrue(s["expected"]["interim_is_estimated_not_realised"])
        self.assertTrue(s["expected"]["ses_netted_before_tranche_allocation"])

    def test_final_realised_severity_and_trueup(self):
        s = self.s
        d = s["defaulted_obligation"]
        equity = s["capital_structure"]["equity"]["thickness_mm"]
        itm = s["expected"]["interim"]
        fin = s["expected"]["final"]

        real_lgd = 1 - d["realised_recovery"]
        realised = d["rona_mm"] * real_lgd
        true_up = realised - itm["gross_estimated_loss_mm"]
        cum_post_ses = realised - itm["ses_available_mm"]
        equity_remaining = equity - min(cum_post_ses, equity)
        mezz_writedown = max(cum_post_ses - equity, 0.0)

        self.assertAlmostEqual(real_lgd, fin["realised_lgd"], places=6)
        self.assertAlmostEqual(realised, fin["realised_loss_mm"], places=6)
        self.assertAlmostEqual(true_up, fin["true_up_mm"], places=6)
        self.assertAlmostEqual(cum_post_ses, fin["cumulative_loss_post_ses_mm"], places=6)
        self.assertAlmostEqual(equity_remaining, fin["equity_remaining_mm"], places=6)
        self.assertAlmostEqual(mezz_writedown, fin["mezz_writedown_mm"], places=6)
        # downturn: realised severity worse than the interim estimate
        self.assertGreater(real_lgd, itm["estimated_lgd"])
        self.assertTrue(s["expected"]["realised_severity_worse_than_estimate_downturn"])
        self.assertTrue(s["expected"]["true_up_can_flow_either_direction"])

    def test_defaulted_excluded_from_forward_pd_lgd_but_stays_in_tieout(self):
        normalize = load_script("normalize_tape")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "canon.csv"
            rep = Path(tmp) / "rep.json"
            status = normalize.main([
                "--tape", str(SCEN / "reference-registry.csv"),
                "--mapping", str(SCEN / "mapping.json"),
                "--out", str(out), "--report", str(rep),
            ])
            self.assertEqual(status, 0)
            r = load_json(rep)
            tie = r.get("tie_out_status")
            if tie is None:
                tie = "OK" if r.get("tie_out_ok") else "FAIL"
            self.assertIn(tie, ("OK", "SKIPPED"))      # defaulted RONA stays in the tie-out
            self.assertEqual(r["rows_out"], 7)         # defaulted name still in the notional
            self.assertEqual(r["defaulted"], 1)

            res = subprocess.run(
                [PY, str(PLUGIN_ROOT / "scripts" / "srt-registry-inputs" / "pd_lgd_weighted_average.py"), str(out)],
                capture_output=True, text=True,
            )
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn("1 excluded", res.stdout)     # defaulted EXCLUDED from forward pool
            self.assertIn("SUM(RONA): 960", res.stdout)
            self.assertTrue(self.s["expected"]["must_exclude_defaulted_from_forward_performing_pd_lgd"])
            self.assertTrue(self.s["expected"]["must_keep_defaulted_in_notional_tieout"])


if __name__ == "__main__":
    unittest.main()
