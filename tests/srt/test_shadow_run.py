"""Tests for the read-only shadow harness (`scripts/srt-review-package/shadow_run.py`).

Added by the 2026-09-11 showcase review (findings C1/T15, C2, C4). Before this file the
harness had no test at all and sat outside the coverage roots, so every number it printed
was unverified. Three things are pinned:

  1. the documented self-test (alpha canonical registry + `shadow-input.example.json`)
     reproduces the exact block: WA PD, WA LGD, the dampened DM, and no stop;
  2. a performing row with no PD is a STOP, as it is everywhere else in the toolkit
     (`normalize_tape` required-field stop, `pd_lgd_weighted_average` "WA PD blocked");
  3. a missing `spread_duration` is reported, not silently booked as a zero spread leg.

Synthetic obligors only.
"""
import contextlib
import csv
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SHADOW = PLUGIN_ROOT / "scripts" / "srt-review-package" / "shadow_run.py"
NORMALIZE = PLUGIN_ROOT / "scripts" / "srt-registry-inputs" / "normalize_tape.py"
ALPHA_TAPE = PLUGIN_ROOT / "assets" / "srt" / "sandbox-scenarios" / "alpha-rollforward" / "reference-registry.csv"
ALPHA_MAPPING = PLUGIN_ROOT / "assets" / "srt" / "adapters" / "issuer-mapping.example.json"
SHADOW_INPUT = PLUGIN_ROOT / "assets" / "srt" / "adapters" / "shadow-input.example.json"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def alpha_canonical(tmp):
    normalize = load(NORMALIZE, "normalize_tape")
    out = tmp / "alpha-canonical.csv"
    with contextlib.redirect_stdout(io.StringIO()):
        code = normalize.main(["--tape", str(ALPHA_TAPE), "--mapping", str(ALPHA_MAPPING), "--out", str(out)])
    assert code == 0, "the alpha self-test registry must normalize cleanly"
    return out


def run_shadow(registry, input_path, tmp):
    shadow = load(SHADOW, "shadow_run")
    report = tmp / "shadow.json"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        shadow.main(["--registry", str(registry), "--input", str(input_path), "--report", str(report)])
    return json.loads(report.read_text(encoding="utf-8")), buf.getvalue()


class AlphaSelfTest(unittest.TestCase):
    """The self-test documented in adapters/adapter-guide.md, pinned to the figures the alpha
    grading key quotes (WA PD 2.20 -> 2.39 %, LGD 58.5 -> 59.7 %, DM 545 - 4 = 541)."""

    def test_exact_block_reproduces_the_alpha_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            report, _ = run_shadow(alpha_canonical(tmp), SHADOW_INPUT, tmp)
        est = report["estimate"]
        self.assertAlmostEqual(est["wa_pd"], 0.0239425, places=7)
        self.assertAlmostEqual(est["wa_lgd"], 0.59695, places=5)
        self.assertEqual(est["valuation_dm_bps"], 541.0)
        self.assertEqual(report["total_rona"], 1000.0)
        self.assertEqual(report["would_stop"], [])
        # the agreement block diffs against the recorded actual in the example input
        self.assertEqual(report["agreement"]["valuation_dm_bps"]["diff_bps"], 0.0)


class MissingPdIsAStop(unittest.TestCase):
    def test_a_performing_row_without_pd_is_reported_as_a_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            canon = alpha_canonical(tmp)
            rows = list(csv.DictReader(canon.open(newline="", encoding="utf-8")))
            rows[0]["pd"] = ""
            blanked = tmp / "alpha-blank-pd.csv"
            with blanked.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
            report, out = run_shadow(blanked, SHADOW_INPUT, tmp)
        self.assertTrue(any("PD" in s for s in report["would_stop"]),
                        f"a missing PD was not a stop; would_stop={report['would_stop']}")
        self.assertNotIn("No stop conditions", out)


class MissingSpreadDurationIsReported(unittest.TestCase):
    def test_spread_leg_is_marked_not_estimated_when_spread_duration_is_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            inp = json.loads(SHADOW_INPUT.read_text(encoding="utf-8"))
            del inp["market"]["spread_duration"]
            inp_path = tmp / "input-no-sd.json"
            inp_path.write_text(json.dumps(inp), encoding="utf-8")
            report, out = run_shadow(alpha_canonical(tmp), inp_path, tmp)
        self.assertIn("spread_duration", out)
        self.assertEqual(report["estimate"]["bridge_pts"]["spread"], "not estimated")


if __name__ == "__main__":
    unittest.main()
