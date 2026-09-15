import re
import unittest
import zipfile
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
ASSETS = PLUGIN_ROOT / "assets" / "srt"


class SrtPluginPackagingTests(unittest.TestCase):
    def test_archival_source_snapshot_is_compressed(self):
        archive = ASSETS / "source-snapshot.zip"
        self.assertTrue(archive.exists(), "dense source snapshot should be stored as a zip archive")
        self.assertFalse(
            (ASSETS / "source-snapshot").exists(),
            "expanded source snapshot should not ship as deferred readable text",
        )

        required = {
            "SKILL.md",
            "AGENTS.md",
            "corpus.map.json",
            "references/process.md",
            "references/model-cell-map.md",
            "references/legal-inputs.md",
            "references/ses.md",
            "references/spreads-dm-calibration.md",
            "scripts/srt-registry-inputs/normalize_tape.py",
            "scripts/srt-registry-inputs/pd_lgd_weighted_average.py",
            "scripts/srt-review-package/shadow_run.py",
            "templates/run-state.json",
            "test_srt_scripts.py",
        }
        with zipfile.ZipFile(archive) as package:
            names = set(package.namelist())
        self.assertEqual(sorted(required - names), [])

    def test_reference_load_index_routes_without_loading_every_reference(self):
        index_path = ASSETS / "reference-load-index.md"
        text = index_path.read_text(encoding="utf-8")

        expected_paths = [
            "references/process.md",
            "references/model-cell-map.md",
            "references/model-input-cheatsheet.md",
            "references/registry-structure.md",
            "references/defaulted-and-nonliquidated-borrowers.md",
            "references/evidence.md",
        ]
        for rel in expected_paths:
            self.assertIn(rel, text)

        self.assertIn("Load exactly one primary reference first", text)
        self.assertIn("Do not bulk-load", text)

    def test_coverage_artifact_is_present_for_plugin_eval(self):
        coverage = PLUGIN_ROOT / "coverage.xml"
        self.assertTrue(coverage.exists(), "coverage.xml should be generated for Plugin Eval coverage scoring")
        text = coverage.read_text(encoding="utf-8")
        match = re.search(r'line-rate="([^"]+)"', text)
        self.assertIsNotNone(match, "coverage.xml should expose a line-rate attribute")
        self.assertGreaterEqual(float(match.group(1)), 0.40)
        # review 2026-09-11 (C21): the runner's seed file is a 1-line placeholder; a real run
        # measures hundreds of lines, so a seed left behind by a crashed run must not pass here.
        valid = re.search(r'lines-valid="(\d+)"', text)
        self.assertIsNotNone(valid, "coverage.xml should expose lines-valid")
        self.assertGreater(int(valid.group(1)), 100, "coverage.xml looks like the pre-run seed, not a measurement")


if __name__ == "__main__":
    unittest.main()
