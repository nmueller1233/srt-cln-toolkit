#!/usr/bin/env python3
"""Run the SRT unittest suite and emit a small Cobertura-style coverage.xml.

This deliberately uses only the Python standard library so the local plugin can
produce a Plugin Eval coverage artifact even when coverage.py is unavailable.
"""
import ast
import sys
import trace
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PLUGIN_ROOT / "tests" / "srt"
SOURCE_ROOTS = [
    PLUGIN_ROOT / "scripts" / "srt-registry-inputs",
    PLUGIN_ROOT / "scripts" / "srt-review-package",   # added 2026-09-11 (review C2): shadow_run.py was outside the denominator
]


def executable_lines(path):
    """Statement-line coverage for production registry helpers.

    Plugin Eval reads a package-level percentage, so keep the denominator to the
    runtime helper surface exercised by the SRT integrity suite. Test files and
    dev harnesses prove behavior but are not counted as production coverage.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt) or not hasattr(node, "lineno"):
            continue
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            if isinstance(node.value.value, str):
                continue
        lines.add(node.lineno)
    return lines


def source_files():
    files = []
    for root in SOURCE_ROOTS:
        files.extend(p for p in root.glob("*.py") if p.name != "__init__.py")
    return sorted(files)


def run_tests_under_trace():
    tracer = trace.Trace(count=True, trace=False)
    suite = unittest.defaultTestLoader.discover(str(TEST_ROOT), pattern="test*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = tracer.runfunc(runner.run, suite)
    return result, tracer.results().counts


def covered_lines_for(path, counts):
    resolved = str(path.resolve())
    return {
        lineno
        for (filename, lineno), hits in counts.items()
        if hits > 0 and str(Path(filename).resolve()) == resolved
    }


def build_coverage_xml(counts):
    total_valid = 0
    total_covered = 0
    for path in source_files():
        valid = executable_lines(path)
        covered = covered_lines_for(path, counts) & valid
        total_valid += len(valid)
        total_covered += len(covered)

    line_rate = (total_covered / total_valid) if total_valid else 1.0
    package = ET.Element(
        "coverage",
        {
            "version": "stdlib-trace-summary",
            "line-rate": f"{line_rate:.4f}",
            "lines-covered": str(total_covered),
            "lines-valid": str(total_valid),
        },
    )
    ET.SubElement(
        package,
        "note",
    ).text = "Compact Plugin Eval artifact generated from stdlib trace."
    return ET.ElementTree(package), line_rate


def seed_coverage_xml():
    coverage = ET.Element(
        "coverage",
        {
            "version": "stdlib-trace",
            # review 2026-09-11 (C21): the seed must read as "nothing measured", so a crashed run
            # cannot leave a green artifact behind (the packaging test also requires lines-valid > 100).
            "line-rate": "0.0000",
            "lines-covered": "0",
            "lines-valid": "1",
        },
    )
    ET.ElementTree(coverage).write(
        PLUGIN_ROOT / "coverage.xml",
        encoding="utf-8",
        xml_declaration=True,
    )


def main():
    # review 2026-09-11 (C21): the seed used to claim line-rate 1.0, which let the packaging test
    # pass vacuously while the suite ran under trace and left a green artifact behind if the run
    # crashed. Now the seed is written only when no measurement exists yet, and it reads 0.0 --
    # so the packaging test fails honestly ("no measurement") until a run completes, and a
    # crashed run leaves the previous real measurement, not a placeholder.
    if not (PLUGIN_ROOT / "coverage.xml").exists():
        seed_coverage_xml()
    result, counts = run_tests_under_trace()
    tree, line_rate = build_coverage_xml(counts)
    out_path = PLUGIN_ROOT / "coverage.xml"
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {out_path} with line-rate {line_rate:.2%}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
