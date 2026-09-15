import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def load_script(name):
    path = PLUGIN_ROOT / "scripts" / "srt-registry-inputs" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WeightedAverageHelperTests(unittest.TestCase):
    def test_to_float_handles_decimal_and_percent_inputs(self):
        helper = load_script("pd_lgd_weighted_average")

        self.assertEqual(helper.to_float("0.025"), 0.025)
        self.assertEqual(helper.to_float("2.5%"), 0.025)
        self.assertEqual(helper.to_float("1,250"), 1250.0)


class NormalizeTapeTests(unittest.TestCase):
    def test_normalize_rows_helper_converts_recovery_and_reports_tie_out(self):
        normalize = load_script("normalize_tape")

        mapping = {
            "source": {"type": "csv"},
            "column_map": {
                "obligor_id": "Obligor",
                "maturity_date": "Maturity Date",
                "rona": "RONA",
                "pd": "PD",
                "recovery": "Recovery",
            },
            "deal_meta": {
                "deal": "Helper Test",
                "currency": "USD",
                "stated_reference_notional": 100,
            },
            "required_fields": ["rona", "maturity_date"],
        }
        rows = [
            {
                "Obligor": "Alpha",
                "Maturity Date": "2029-03-20",
                "RONA": "100",
                "PD": "2.5%",
                "Recovery": "40%",
            }
        ]

        normalized, report = normalize.normalize_rows(rows, list(rows[0].keys()), mapping)

        self.assertEqual(normalized[0]["lgd"], 0.6)
        self.assertEqual(normalized[0]["pd"], 0.025)
        self.assertEqual(report["tie_out_status"], "OK")
        self.assertEqual(report["stops"], [])

    def test_recovery_converts_to_lgd_and_ties_rona(self):
        normalize = load_script("normalize_tape")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            tape_path = tmp_path / "raw.csv"
            mapping_path = tmp_path / "mapping.json"
            out_path = tmp_path / "canonical.csv"
            report_path = tmp_path / "report.json"

            with tape_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["Obligor", "Maturity Date", "RONA", "PD", "Recovery"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "Obligor": "Alpha",
                        "Maturity Date": "2029-03-20",
                        "RONA": "100",
                        "PD": "0.02",
                        "Recovery": "0.40",
                    }
                )

            mapping_path.write_text(
                json.dumps(
                    {
                        "source": {"type": "csv"},
                        "column_map": {
                            "obligor_id": "Obligor",
                            "maturity_date": "Maturity Date",
                            "rona": "RONA",
                            "pd": "PD",
                            "recovery": "Recovery",
                        },
                        "deal_meta": {
                            "deal": "Unit Test",
                            "currency": "USD",
                            "stated_reference_notional": 100,
                        },
                        "required_fields": ["rona", "maturity_date"],
                    }
                ),
                encoding="utf-8",
            )

            status = normalize.main(
                [
                    "--tape",
                    str(tape_path),
                    "--mapping",
                    str(mapping_path),
                    "--out",
                    str(out_path),
                    "--report",
                    str(report_path),
                ]
            )

            self.assertEqual(status, 0)
            with out_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["lgd"], "0.6")
            report = json.loads(report_path.read_text(encoding="utf-8"))
            tie_ok = report.get("tie_out_ok")
            if tie_ok is None and isinstance(report.get("tie_out"), dict):
                tie_ok = report["tie_out"].get("ok")
            if tie_ok is None and "tie_out_status" in report:
                tie_ok = report["tie_out_status"] == "OK"
            self.assertTrue(tie_ok)


if __name__ == "__main__":
    unittest.main()
