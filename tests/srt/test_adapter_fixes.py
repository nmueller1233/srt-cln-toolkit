"""Adapter shape-guard regression suite.

Regression suite for the adapter shape-guard fixes to normalize_tape.py /
pd_lgd_weighted_average.py (seven tests covering the 23 review checks of the original
code review; the review's own script is not part of this repository).
It guards the shape-defending fixes that a byte-identical copy of a *stale* source
would silently drop: percent->decimal, [0,1] range guard, totals/footer-row skip,
secured-vs-unsecured, exact canonical column resolution, and LGD-direct fallback.

Runs the scripts the way a host would (subprocess CLI). Fixtures are throwaway temp
files; no repo artifact is written.
"""
import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = PLUGIN_ROOT / "scripts" / "srt-registry-inputs"
NORM = SCRIPTS / "normalize_tape.py"
PDLGD = SCRIPTS / "pd_lgd_weighted_average.py"
SCEN = PLUGIN_ROOT / "assets" / "srt" / "sandbox-scenarios"
EXMAP = PLUGIN_ROOT / "assets" / "srt" / "adapters" / "issuer-mapping.example.json"
PY = sys.executable


def run(*args):
    p = subprocess.run([PY, *[str(a) for a in args]], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def read_canon(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["obligor_id"]: r for r in csv.DictReader(f)}


class AdapterShapeGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="srt_adapter_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _w(self, name, headers, rows):
        p = Path(self.tmp) / name
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for r in rows:
                w.writerow(r)
        return p

    def _mini_map(self):
        p = Path(self.tmp) / "mini-map.json"
        p.write_text(json.dumps({
            "issuer": "MINI", "source": {"type": "csv"},
            "column_map": {"obligor_id": "Name", "obligor_name": "Name", "rona": "Notional",
                           "pd": "PD", "recovery": "Recovery", "seniority": "Seniority",
                           "maturity_date": "Maturity"},
            "transforms": {"date_formats": ["%Y-%m-%d"]},
            "deal_meta": {"deal": "Mini", "currency": "USD", "stated_reference_notional": 200},
            "required_fields": ["rona", "maturity_date"], "tie_out": {"tolerance_pct": 0.005},
        }), encoding="utf-8")
        return p

    # 1) Alpha normalizes, ties out, and secured flag does not read 'unsecured' as secured.
    def test_alpha_normalizes_and_secured_respects_unsecured(self):
        out = Path(self.tmp) / "alpha-canon.csv"
        rc, log = run(NORM, "--tape", SCEN / "alpha-rollforward" / "reference-registry.csv",
                      "--mapping", EXMAP, "--out", out)
        self.assertEqual(rc, 0, log)
        self.assertIn("vs stated 1,000", log)
        self.assertIn("OK", log)
        canon = read_canon(out)
        self.assertEqual(canon["Alpha Industrials Inc"]["secured"], "True", canon["Alpha Industrials Inc"])
        self.assertEqual(canon["Cobalt Auto Parts"]["secured"], "False", canon["Cobalt Auto Parts"])
        self.assertEqual(canon["Kestrel Media"]["secured"], "False", canon["Kestrel Media"])

    # 2) pd_lgd resolves the EXACT 'pd' column (not a bare substring) and weights correctly.
    def test_pd_lgd_exact_column_resolution_and_weighted_averages(self):
        out = Path(self.tmp) / "alpha-canon.csv"
        rc, _ = run(NORM, "--tape", SCEN / "alpha-rollforward" / "reference-registry.csv",
                    "--mapping", EXMAP, "--out", out)
        self.assertEqual(rc, 0)
        rc, log = run(PDLGD, out)
        self.assertEqual(rc, 0, log)
        self.assertIn("PD='pd'", log)
        self.assertIn("2.39", log)
        self.assertIn("59.6", log)

    # 3) Delta: SUM(rona) does not reconcile -> STOP (exit 1).
    def test_delta_stops_on_reconcile_failure(self):
        rc, log = run(NORM, "--tape", SCEN / "delta-stop" / "reference-registry.csv",
                      "--mapping", EXMAP, "--out", Path(self.tmp) / "delta-canon.csv")
        self.assertEqual(rc, 1, log)
        self.assertIn("reconcile", log.lower())

    # 4) pd_lgd LGD-direct fallback: recovery blank but LGD present -> use LGD, no false STOP.
    def test_pd_lgd_lgd_direct_fallback(self):
        p = self._w("lgd-direct.csv", ["obligor_id", "rona", "pd", "recovery", "lgd", "status"],
                    [["A", "100", "0.02", "", "0.55", "Performing"],
                     ["B", "100", "0.03", "", "0.65", "Performing"]])
        rc, log = run(PDLGD, p)
        self.assertEqual(rc, 0, log)
        self.assertIn("WA LGD column", log)
        self.assertIn("60.0000%", log)

    # 5) Percent ("40%" -> 0.40) AND totals/footer row skipped (not ingested as an obligor).
    def test_percent_conversion_and_totals_row_skipped(self):
        tape = self._w("mini.csv", ["Name", "Notional", "PD", "Recovery", "Seniority", "Maturity"],
                       [["Acme Corp", "100", "0.02", "40%", "Senior Unsecured", "2029-06-30"],
                        ["Beta Ltd", "100", "0.03", "0.45", "Senior Secured", "2030-03-31"],
                        ["Total", "200", "", "", "", ""]])
        out = Path(self.tmp) / "mini-canon.csv"
        rc, log = run(NORM, "--tape", tape, "--mapping", self._mini_map(), "--out", out)
        self.assertEqual(rc, 0, log)
        self.assertIn("non-obligor skipped", log)
        mc = read_canon(out)
        self.assertEqual(len(mc), 2, list(mc))
        self.assertEqual(mc["Acme Corp"]["recovery"], "0.4")
        self.assertAlmostEqual(float(mc["Acme Corp"]["lgd"]), 0.6, places=9)
        self.assertIn("-> OK", log)

    # 6) Range guard: an impossible value (150% recovery) is a STOP, not a silent number.
    def test_range_guard_stops_on_value_outside_unit_interval(self):
        tape = self._w("bad.csv", ["Name", "Notional", "PD", "Recovery", "Seniority", "Maturity"],
                       [["Acme Corp", "100", "0.02", "150%", "Senior Secured", "2029-06-30"]])
        rc, log = run(NORM, "--tape", tape, "--mapping", self._mini_map(), "--out", Path(self.tmp) / "bad-out.csv")
        self.assertEqual(rc, 1, log)
        self.assertIn("outside [0,1]", log)

    # 7) A mapped (non-required) column missing from the tape header is surfaced, not silently blank.
    def test_missing_mapped_column_is_surfaced(self):
        tape = self._w("renamed.csv", ["Name", "Notional", "PD", "RecoveryPct", "Seniority", "Maturity"],
                       [["Acme Corp", "100", "0.02", "0.40", "Senior Secured", "2029-06-30"]])
        rc, log = run(NORM, "--tape", tape, "--mapping", self._mini_map(), "--out", Path(self.tmp) / "ren-out.csv")
        self.assertIn("not found in tape header", log)


if __name__ == "__main__":
    unittest.main()
