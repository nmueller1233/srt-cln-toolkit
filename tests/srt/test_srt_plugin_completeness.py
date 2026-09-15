import filecmp
import tempfile
import unittest
import zipfile
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ZIP = PLUGIN_ROOT / "assets" / "srt" / "source-snapshot.zip"


class SrtPluginCompletenessTests(unittest.TestCase):
    def test_source_snapshot_contains_dense_original_skill_module(self):
        required = [
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
        ]
        with zipfile.ZipFile(SNAPSHOT_ZIP) as package:
            names = set(package.namelist())
        missing = [rel for rel in required if rel not in names]
        self.assertEqual(missing, [])

    def test_runtime_assets_match_snapshot_for_core_dense_references(self):
        pairs = [
            ("references/process.md", "assets/srt/references/process.md"),
            ("references/model-cell-map.md", "assets/srt/references/model-cell-map.md"),
            ("references/legal-inputs.md", "assets/srt/references/legal-inputs.md"),
            ("references/ses.md", "assets/srt/references/ses.md"),
            ("references/spreads-dm-calibration.md", "assets/srt/references/spreads-dm-calibration.md"),
            ("scripts/srt-registry-inputs/normalize_tape.py", "scripts/srt-registry-inputs/normalize_tape.py"),
            ("scripts/srt-registry-inputs/pd_lgd_weighted_average.py", "scripts/srt-registry-inputs/pd_lgd_weighted_average.py"),
            ("scripts/srt-review-package/shadow_run.py", "scripts/srt-review-package/shadow_run.py"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(SNAPSHOT_ZIP) as package:
                package.extractall(tmp)
            snapshot = Path(tmp)
            mismatches = []
            for snapshot_rel, plugin_rel in pairs:
                if not filecmp.cmp(snapshot / snapshot_rel, PLUGIN_ROOT / plugin_rel, shallow=False):
                    mismatches.append((snapshot_rel, plugin_rel))
            self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
