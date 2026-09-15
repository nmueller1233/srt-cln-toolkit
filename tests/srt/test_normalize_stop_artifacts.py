"""What a STOPPED normalize run leaves on disk, and what a silent rename reports.

Added by the 2026-09-11 showcase review (findings C9 and C11, class B):
  - a run that STOPs must not leave a complete `canonical-registry.csv` under the requested
    name, because a downstream step that checks for the file (not the exit code) would
    proceed on fabricated-by-omission data;
  - a duplicated obligor id is renamed `<id> #2`; that must be reported, not silent.

Synthetic obligors only.
"""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN_ROOT / "scripts" / "srt-registry-inputs" / "normalize_tape.py"


def load_normalize():
    spec = importlib.util.spec_from_file_location("normalize_tape", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HEADER = ["Obligor", "Maturity Date", "RONA", "PD", "Recovery"]
MAPPING = {
    "source": {"type": "csv"},
    "column_map": {"obligor_name": "Obligor", "maturity_date": "Maturity Date",
                "rona": "RONA", "pd": "PD", "recovery": "Recovery"},
    "deal_meta": {"deal": "T", "stated_reference_notional": 0},
    "required_fields": ["rona", "maturity_date", "pd"],
}


def run(rows, mapping):
    normalize = load_normalize()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tape, mp, out, rep = tmp / "raw.csv", tmp / "map.json", tmp / "canonical.csv", tmp / "report.json"
        with tape.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            w.writerows(rows)
        mp.write_text(json.dumps(mapping), encoding="utf-8")
        code = normalize.main(["--tape", str(tape), "--mapping", str(mp), "--out", str(out), "--report", str(rep)])
        report = json.loads(rep.read_text(encoding="utf-8"))
        on_disk = sorted(p.name for p in tmp.iterdir())
        return code, report, on_disk


class StoppedRunArtifacts(unittest.TestCase):
    def test_a_stopped_run_does_not_leave_the_canonical_file_under_the_requested_name(self):
        rows = [{"Obligor": "Alpha", "Maturity Date": "2029-03-20", "RONA": "100", "PD": "0.02", "Recovery": "0.40"},
                {"Obligor": "Beta", "Maturity Date": "2029-03-20", "RONA": "50", "PD": "", "Recovery": "0.40"}]
        code, report, on_disk = run(rows, MAPPING)
        self.assertEqual(code, 1)
        self.assertTrue(report["stops"])
        self.assertNotIn("canonical.csv", on_disk, "a STOPPED run wrote the canonical file under the requested name")
        self.assertIn("canonical.STOPPED.csv", on_disk, "the stopped rows should still be inspectable")
        self.assertTrue(report["canonical"].endswith("canonical.STOPPED.csv"))

    def test_a_clean_run_writes_the_canonical_file_under_the_requested_name(self):
        rows = [{"Obligor": "Alpha", "Maturity Date": "2029-03-20", "RONA": "100", "PD": "0.02", "Recovery": "0.40"}]
        code, report, on_disk = run(rows, MAPPING)
        self.assertEqual(code, 0)
        self.assertIn("canonical.csv", on_disk)
        self.assertNotIn("canonical.STOPPED.csv", on_disk)


class DuplicateObligorIds(unittest.TestCase):
    def test_a_duplicated_obligor_id_is_reported_in_the_notes(self):
        rows = [{"Obligor": "Beta", "Maturity Date": "2029-03-20", "RONA": "100", "PD": "0.02", "Recovery": "0.40"},
                {"Obligor": "Beta", "Maturity Date": "2030-03-20", "RONA": "50", "PD": "0.03", "Recovery": "0.40"}]
        code, report, _ = run(rows, MAPPING)
        self.assertEqual(code, 0)
        self.assertTrue(any("Beta" in n and "#2" in n for n in report["notes"]),
                        f"duplicate id renamed silently; notes were {report['notes']}")


class UnclassifiedStatusValues(unittest.TestCase):
    def test_status_values_outside_the_defaulted_list_are_named_in_the_notes(self):
        mapping = dict(MAPPING)
        mapping["column_map"] = dict(MAPPING["column_map"], status="Status")
        header = HEADER + ["Status"]
        rows = [{"Obligor": "Alpha", "Maturity Date": "2029-03-20", "RONA": "100", "PD": "0.02", "Recovery": "0.40", "Status": "Performing"},
                {"Obligor": "Gamma", "Maturity Date": "2029-03-20", "RONA": "50", "PD": "0.02", "Recovery": "0.40", "Status": "Restructured"}]
        normalize = load_normalize()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            tape, mp, out, rep = tmp / "raw.csv", tmp / "map.json", tmp / "canonical.csv", tmp / "report.json"
            with tape.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=header)
                w.writeheader()
                w.writerows(rows)
            mp.write_text(json.dumps(mapping), encoding="utf-8")
            code = normalize.main(["--tape", str(tape), "--mapping", str(mp), "--out", str(out), "--report", str(rep)])
            report = json.loads(rep.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertTrue(any("Restructured" in n for n in report["notes"]),
                        f"an unclassified status was treated as Performing without a note; notes were {report['notes']}")


if __name__ == "__main__":
    unittest.main()
