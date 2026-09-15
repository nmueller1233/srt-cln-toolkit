"""Content-contract checks for the redesigned analyst-task skill library."""
import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
REFS = ROOT / "assets" / "srt" / "references"
RUNTIME_TEXT_ROOTS = [SKILLS, REFS]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def _forbidden_terms():
    """Exported copy: the owner-name and example terms are not shipped; they come from the environment."""
    terms = [t for t in os.environ.get("SHOWCASE_FORBIDDEN_TERMS", "").split("|") if t]
    if not terms:
        raise unittest.SkipTest("forbidden-term list not shipped (set SHOWCASE_FORBIDDEN_TERMS=term1|term2)")
    return [r"(?i)(?<![a-z])" + re.escape(t) + r"(?![a-z])" for t in terms]


class SkillRedesignContractTests(unittest.TestCase):
    def test_expected_skill_library_exists(self):
        expected = {
            "srt-quarterly-update",
            "srt-calibration",
            "srt-legal-deal-mechanics",
            "srt-registry-inputs",
            "srt-quarterly-model-update",
            "srt-review-package",
            "srt-difficulties",
            "srt-copula",
        }
        actual = {p.parent.name for p in SKILLS.glob("*/SKILL.md")}
        self.assertEqual(actual, expected)
        self.assertFalse((SKILLS / "srt-source-inputs" / "SKILL.md").exists())
        self.assertFalse((SKILLS / "srt-model-update" / "SKILL.md").exists())

    def test_router_asks_calibration_or_quarterly_update(self):
        text = read("skills/srt-quarterly-update/SKILL.md")
        self.assertIn("Is this a new-deal calibration or a quarterly update?", text)
        for skill in [
            "srt-calibration",
            "srt-legal-deal-mechanics",
            "srt-registry-inputs",
            "srt-quarterly-model-update",
            "srt-review-package",
            "srt-difficulties",
            "srt-copula",
        ]:
            self.assertIn(skill, text)

    def test_calibration_has_process_inputs_dm_review_and_legal_doc_request(self):
        text = read("skills/srt-calibration/SKILL.md")
        for needle in [
            "calibration process, the required inputs / cell map, or reviewing whether a calibrated DM looks reasonable",
            "ask for the legal document",
            "L30",
            "H36",
            "D10 = D14",
            "CDS / CDX / iTraxx alignment is not a calibration-DM issue",
        ]:
            self.assertIn(needle, text)

    def test_quarterly_update_has_spread_change_language(self):
        text = read("skills/srt-quarterly-model-update/SKILL.md")
        for needle in ["CDS / CDX / iTraxx", "Spread Analysis", "D8", "L32", "L34"]:
            self.assertIn(needle, text)
        self.assertIn("Do not re-solve `L30` during a quarterly update", text)

    def test_reviewer_triggers_are_limited_to_agreed_risks(self):
        text = read("skills/srt-review-package/SKILL.md")
        flat = " ".join(text.split())  # collapse markdown line-wrapping before matching
        # Review is reserved for the three genuinely subjective valuation calls;
        # legal / model / registry questions are answered, not escalated.
        for needle in [
            "defaulted/non-liquidated severity with no governing contract",
            "benchmark selection",
            "spread change",
            "a second reviewer",
            "Do not escalate a fixed legal term",
        ]:
            self.assertIn(needle, flat)
        # Reviewer language stays generic -- never "your reviewer" (a specific person).
        self.assertNotIn("your reviewer", flat.lower())

    def test_no_user_name_or_real_example_in_runtime_text(self):
        bad = []
        # review 2026-09-11 (C22): JSON under assets/ is scanned too, and the owner's name is
        # forbidden inside identifiers as well (`..._with_<name>` keys), not only as a word.
        roots = list(RUNTIME_TEXT_ROOTS) + [ROOT / "assets" / "srt"]
        seen = set()
        for root in roots:
            for pattern in ("*.md", "*.json"):
                for path in root.rglob(pattern):
                    if path in seen:
                        continue
                    seen.add(path)
                    text = path.read_text(encoding="utf-8")
                    forbidden = _forbidden_terms()
                    if any(re.search(term, text) for term in forbidden):
                        bad.append(str(path.relative_to(ROOT)))
        self.assertEqual(bad, [])

    def test_model_map_critical_cells_remain_present(self):
        text = read("assets/srt/references/model-cell-map.md")
        for needle in ["D10", "D14", "D18", "H10", "H11", "L30", "L32", "L34", "M34", "H36", "D3", "D4"]:
            self.assertIn(needle, text)
        self.assertIn("D8", read("assets/srt/references/model-input-cheatsheet.md"))
        self.assertIn("Spread Analysis", read("assets/srt/references/model-input-cheatsheet.md"))

    def test_common_questions_focuses_on_tricky_confusions(self):
        text = read("skills/srt-difficulties/SKILL.md")
        reference = read("assets/srt/references/common-confusions.md")
        for needle in [
            "Negative accrued interest",
            "split-tranche amortization",
            "Exposure at default",
            "CDS coupon",
            "On-the-run benchmark",
            "CDX/iTraxx index constituents",
            "newly defaulted and non-liquidated",
        ]:
            self.assertIn(needle, text + reference)
        self.assertIn("longer theory-driven explanation", text)
        self.assertIn("CDS / CDX / iTraxx alignment is not a calibration-DM suspicion test", text)

    def test_copula_skill_is_conceptual_and_report_only(self):
        text = read("skills/srt-copula/SKILL.md").lower()
        for needle in ["report-only", "long correlation", "short correlation", "open for others"]:
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
