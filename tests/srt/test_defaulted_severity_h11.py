"""H11 (defaulted / non-liquidated) severity -- golden regression.

A newly defaulted, not-yet-liquidated name carries an ESTIMATED severity `H11`, set as
`1 - RONA-weighted recovery` across the defaulted/non-liquidated tab (a contractual
recovery, or the secondary price of the most comparable bond as a market-implied
recovery). The quarterly update reuses `pd_lgd_weighted_average.py --include-defaulted`
for exactly this. This locks the arithmetic and the operator conventions so the path
can't silently drift. See references/defaulted-and-nonliquidated-borrowers.md and
references/pd-lgd-severity.md.
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
    if (_cand / "pd_lgd_weighted_average.py").exists():
        sys.path.insert(0, str(_cand))
        break
import pd_lgd_weighted_average as pld  # noqa: E402


def _write_csv(rows, header):
    fd = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                     newline="", encoding="utf-8")
    with fd:
        writer = csv.DictWriter(fd, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    return fd.name


class H11UnitGolden(unittest.TestCase):
    def test_two_name_weighted_recovery_and_severity(self):
        # 40% recovery on 60mm + 30% recovery on 40mm -> WA recovery 36% -> H11 severity 64%
        incl = [({"recovery": "0.40"}, 60.0, "Acme"), ({"recovery": "0.30"}, 40.0, "Beta")]
        wa, missing = pld.weighted_average(incl, 100.0, "recovery")
        self.assertEqual(missing, [])
        self.assertAlmostEqual(wa, 0.36, places=10)
        self.assertAlmostEqual(1 - wa, 0.64, places=10)   # H11

    def test_single_name_severity_is_one_minus_price(self):
        # comparable-bond secondary price of 55 cents on the dollar -> severity 45%
        incl = [({"recovery": "55%"}, 25.0, "Obligor-3")]
        wa, _ = pld.weighted_average(incl, 25.0, "recovery")
        self.assertAlmostEqual(1 - wa, 0.45, places=10)


class H11Integration(unittest.TestCase):
    def _csv(self, rows):
        path = _write_csv(rows, ["obligor_id", "rona", "recovery", "status"])
        self.addCleanup(os.unlink, path)
        return path

    def test_include_defaulted_flag_drives_the_h11_run(self):
        path = self._csv([
            {"obligor_id": "Acme", "rona": "60", "recovery": "0.40", "status": "Defaulted"},
            {"obligor_id": "Beta", "rona": "40", "recovery": "0.30", "status": "Defaulted"},
        ])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = pld.main([path, "--include-defaulted"])
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("WA LGD   : 64.0000%", out)   # H11 severity
        self.assertIn("WA recov : 36.0000%", out)

    def test_defaulted_only_without_flag_stops_not_fabricates(self):
        """Without --include-defaulted a defaulted-only tab excludes everything -> error
        (exit 2), never a silent wrong number."""
        path = self._csv([
            {"obligor_id": "Acme", "rona": "60", "recovery": "0.40", "status": "Defaulted"},
        ])
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = pld.main([path])
        self.assertEqual(code, 2)
        self.assertIn("SUM(RONA) is zero", err.getvalue())

    def test_rona_weighting_not_equal_weighting(self):
        """The large name must dominate: RONA-weighted recovery .39 -> severity 61%,
        NOT the equal-weight recovery .35 -> 65%."""
        path = self._csv([
            {"obligor_id": "Big", "rona": "90", "recovery": "0.40", "status": "Defaulted"},
            {"obligor_id": "Small", "rona": "10", "recovery": "0.30", "status": "Defaulted"},
        ])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pld.main([path, "--include-defaulted"])
        self.assertIn("WA LGD   : 61.0000%", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
