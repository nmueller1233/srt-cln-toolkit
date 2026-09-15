"""Reference-index integrity — guards the progressive-disclosure router.

The load-index is the authoritative router: lane skills keep only their core
references inline and defer the rest to it. That design only holds if every
reference is actually routed by the index and every linked path resolves. This test
fails if someone adds a reference without routing it (the exact drift that left
cln-aggregation / benchmark-spread-pulling / the theory primer unreachable before),
or breaks an asset link in a lane skill.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets" / "srt"
INDEX = ASSETS / "reference-load-index.md"
SKILLS = list((ROOT / "skills").glob("*/SKILL.md"))


class ReferenceIndexIntegrityTests(unittest.TestCase):
    def test_lane_asset_links_resolve(self):
        path_re = re.compile(r"\.\./\.\./assets/srt/([A-Za-z0-9_./-]+)")
        missing = []
        for sk in SKILLS:
            for rel in path_re.findall(sk.read_text(encoding="utf-8")):
                rel = rel.rstrip(").,`")
                if not (ASSETS / rel).exists():
                    missing.append(f"{sk.parent.name} -> {rel}")
        self.assertEqual(missing, [], f"broken asset links in lane skills: {missing}")

    def test_every_reference_is_routed_by_the_index(self):
        idx = INDEX.read_text(encoding="utf-8")
        routed = set(re.findall(r"references/([a-z0-9-]+\.md)", idx))
        on_disk = {p.name for p in (ASSETS / "references").glob("*.md")}
        orphans = sorted(on_disk - routed)
        self.assertEqual(orphans, [], f"references not reachable via the load-index: {orphans}")

    def test_index_paths_resolve(self):
        idx = INDEX.read_text(encoding="utf-8")
        missing = [rel for rel in re.findall(r"(?:references|templates|adapters)/[A-Za-z0-9_.-]+", idx)
                   if not (ASSETS / rel).exists()]
        self.assertEqual(missing, [], f"load-index points at missing files: {missing}")

    def test_packaging_invariants_present(self):
        idx = INDEX.read_text(encoding="utf-8")
        for needle in ("Load exactly one primary reference first", "Do not bulk-load"):
            self.assertIn(needle, idx)


if __name__ == "__main__":
    unittest.main()
