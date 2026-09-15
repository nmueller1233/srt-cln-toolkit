"""The Bravo (SES-bearing, EUR) sandbox scenario run through the real scripts.

Added by the 2026-09-11 showcase review (finding C16): the Bravo folder was documentation only.
This test normalizes its registry with `bravo-ses/mapping.json`, ties SUM(RONA) to the stated
1,000 (the defaulted name counts toward the tie-out), then runs the RONA-weighted PD/LGD helper
and checks that the defaulted name is excluded from the forward-performing figures.

Hand check (performing pool 970): WA PD = 18.435 / 970 = 1.9005 %; WA recovery = 405.85 / 970
= 41.84 % so WA LGD = 58.16 %.
"""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = PLUGIN_ROOT / "scripts" / "srt-registry-inputs"
BRAVO = PLUGIN_ROOT / "assets" / "srt" / "sandbox-scenarios" / "bravo-ses"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BravoScenario(unittest.TestCase):
    def test_normalize_ties_out_and_pd_lgd_excludes_the_defaulted_name(self):
        normalize, pd_lgd = load("normalize_tape"), load("pd_lgd_weighted_average")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            out, rep = tmp / "bravo-canonical.csv", tmp / "bravo-report.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = normalize.main(["--tape", str(BRAVO / "reference-registry.csv"),
                                       "--mapping", str(BRAVO / "mapping.json"),
                                       "--out", str(out), "--report", str(rep)])
            self.assertEqual(code, 0)
            report = json.loads(rep.read_text(encoding="utf-8"))
            self.assertEqual(report["stops"], [])
            self.assertEqual(report["tie_out_status"], "OK")
            self.assertEqual(report["rows_out"], 12)

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = pd_lgd.main([str(out)])
            text = buf.getvalue()
        self.assertEqual(code, 0, text)
        self.assertIn("11 included, 1 excluded (defaulted)", text)
        self.assertIn("SUM(RONA): 970", text)
        self.assertIn("WA PD    : 1.9005%", text)
        self.assertIn("WA LGD   : 58.1598%", text)


if __name__ == "__main__":
    unittest.main()
