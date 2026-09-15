import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = PLUGIN_ROOT / "assets" / "srt" / "sandbox-scenarios"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_script(name):
    path = PLUGIN_ROOT / "scripts" / "srt-registry-inputs" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SrtSandboxScenarioTests(unittest.TestCase):
    def test_ses_hardcoded_prior_quarter_and_new_default_nets_loss_first(self):
        scenario = load_json(SCENARIO_ROOT / "ses-hardcoded-default" / "scenario.json")
        ses = scenario["ses"]
        default = scenario["new_default_obligation"]
        expected = scenario["expected"]

        accrual = ses["annual_rate"] * ses["quarter_fraction"] * ses["performing_balance"]
        available = ses["brought_forward_balance"] + accrual
        gross_loss = default["rona"] * default["lgd"]
        residual = max(gross_loss - available, 0)

        self.assertTrue(ses["present"])
        self.assertTrue(ses["prior_quarter_value_was_hardcoded"])
        self.assertEqual(default["status"], "Defaulted")
        self.assertAlmostEqual(accrual, expected["ses_accrual"], places=6)
        self.assertAlmostEqual(available, expected["ses_available"], places=6)
        self.assertAlmostEqual(gross_loss, expected["gross_realized_loss"], places=6)
        self.assertAlmostEqual(residual, expected["residual_loss_to_tranche"], places=6)
        self.assertTrue(expected["must_not_reuse_hardcoded_prior_quarter_ses"])
        self.assertTrue(expected["performing_pool_excludes_default"])

    def test_new_deal_is_calibration_not_roll_forward(self):
        scenario = load_json(SCENARIO_ROOT / "new-deal" / "scenario.json")
        expected = scenario["expected"]

        self.assertEqual(scenario["run_type"], "new_deal")
        self.assertFalse(expected["classify_as_roll_forward"])
        self.assertTrue(expected["calibrate_origination_dm_once"])
        self.assertTrue(expected["do_not_roll_prior_spread"])
        self.assertEqual(expected["goal_seek_target"], "equity_clean_price_to_par")
        for tranche in scenario["tranches"]:
            self.assertGreater(tranche["margin_decimal"], 0)
            self.assertLess(tranche["margin_decimal"], 1)

    def test_lgd_only_registry_stops_on_missing_pd_requirement(self):
        normalize = load_script("normalize_tape")
        scenario_dir = SCENARIO_ROOT / "lgd-only-registry"

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "canonical.csv"
            report = Path(tmp) / "report.json"
            status = normalize.main(
                [
                    "--tape",
                    str(scenario_dir / "reference-registry.csv"),
                    "--mapping",
                    str(scenario_dir / "mapping.json"),
                    "--out",
                    str(out),
                    "--report",
                    str(report),
                ]
            )

            self.assertEqual(status, 1)
            details = load_json(report)
            tie_ok = details.get("tie_out_ok")
            if tie_ok is None and "tie_out_status" in details:
                tie_ok = details["tie_out_status"] in ("OK", "SKIPPED")
            self.assertTrue(tie_ok)
            stops = details.get("stops", details.get("problems", []))
            self.assertIn("missing required field 'pd'", "\n".join(stops))
            # since 2026-09-11 (review C9) a STOPPED run writes its rows to <out>.STOPPED.csv,
            # never to <out>; the report names the file that was written.
            self.assertFalse(out.exists(), "a STOPPED run must not leave canonical.csv under the requested name")
            stopped = Path(details["canonical"])
            self.assertTrue(stopped.name.endswith(".STOPPED.csv"))
            with stopped.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["lgd"], "0.58")

    def test_sequential_trigger_requires_waterfall_change_or_review_stop(self):
        scenario = load_json(SCENARIO_ROOT / "sequential-trigger" / "scenario.json")
        trigger = scenario["trigger"]
        waterfall = scenario["payment_waterfall"]
        expected = scenario["expected"]

        self.assertTrue(trigger["occurred_this_quarter"])
        self.assertGreater(trigger["current_level"], trigger["threshold"])
        self.assertEqual(waterfall["prior"], "pro_rata")
        self.assertEqual(waterfall["current"], "sequential")
        self.assertTrue(expected["must_not_continue_pro_rata"])
        self.assertTrue(expected["must_update_payment_waterfall_or_stop_for_human_review"])
        self.assertTrue(expected["mark_requires_trigger_attribution"])
        self.assertFalse(expected["report_ready_without_review"])


if __name__ == "__main__":
    unittest.main()
