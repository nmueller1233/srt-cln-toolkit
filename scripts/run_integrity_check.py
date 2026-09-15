#!/usr/bin/env python3
"""Integrity check -- run the SRT suite and make SKIPPED tests loud and FATAL.

The danger this guards against is NOT a failing test. It is a green run that
silently SKIPPED the workbook-bound tests, so "all pass" hides that the important
checks never executed.

This runner derives what SHOULD run from the environment (corpus.map.json +
openpyxl). If the machine is fully provisioned (both workbooks resolve and
openpyxl is installed) then EVERY test must run -- any skip is treated as a bug
(e.g. a test that can't find a moved script) and fails the run. On a portable
host that legitimately lacks the live workbooks, the skipped tests are reported
loudly but allowed.

It reuses scripts/run_srt_tests_with_coverage.py so it also keeps writing
coverage.xml (which test_plugin_packaging.py asserts exists) -- one runner, no
drift.

Usage:
    python scripts/run_integrity_check.py
    (on Windows: set PYTHONIOENCODING=utf-8 first)

Exit code: 0 = VERIFIED (or partially verified on a portable host), 1 = NOT
VERIFIED (a failure, an error, or an unexpected skip).
"""
import importlib.util
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_srt_tests_with_coverage as cov  # noqa: E402  (reuse the coverage runner)

CORPUS_MAP = PLUGIN_ROOT / "assets" / "srt" / "corpus.map.json"
LINE = "=" * 72


def preflight():
    """Resolve what this machine can actually verify."""
    caps = {
        "openpyxl": importlib.util.find_spec("openpyxl") is not None,
        "corpus_map": CORPUS_MAP.exists(),
        "srt_dcf": False,
        "cln": False,
        "srt_dcf_path": None,
        "cln_path": None,
    }
    if caps["corpus_map"]:
        try:
            cm = json.loads(CORPUS_MAP.read_text(encoding="utf-8"))
            root = Path(cm.get("corpus_root", ""))
            ms = cm.get("model_skeleton", {})
            if ms.get("srt_dcf_model"):
                p = root / ms["srt_dcf_model"]
                caps["srt_dcf_path"], caps["srt_dcf"] = p, p.exists()
            if ms.get("cln_performance_curve"):
                p = root / ms["cln_performance_curve"]
                caps["cln_path"], caps["cln"] = p, p.exists()
        except Exception as exc:  # corrupt corpus.map.json -- say so, don't crash
            caps["error"] = str(exc)
    caps["fully_provisioned"] = caps["openpyxl"] and caps["srt_dcf"] and caps["cln"]
    return caps


def _mark(ok):
    return "[ OK ]    " if ok else "[MISSING] "


def print_preflight(caps):
    print(LINE)
    print("INTEGRITY CHECK -- SRT plugin")
    print(LINE)
    print("Capabilities (what this machine can actually verify):")
    print(f"  {_mark(caps['openpyxl'])} openpyxl installed")
    print(f"  {_mark(caps['corpus_map'])} corpus.map.json found")
    print(f"  {_mark(caps['srt_dcf'])} Srt dcf.xlsm resolves"
          + (f"  ->  {caps['srt_dcf_path']}" if caps["srt_dcf_path"] else ""))
    print(f"  {_mark(caps['cln'])} cln.xlsx resolves"
          + (f"  ->  {caps['cln_path']}" if caps["cln_path"] else ""))
    if caps.get("error"):
        print(f"  [WARN] corpus.map.json could not be parsed: {caps['error']}")
    if caps["fully_provisioned"]:
        print("  MODE: FULLY PROVISIONED -- every test must run; ANY skip is a bug.")
    else:
        print("  MODE: PORTABLE HOST -- workbook-bound tests may legitimately skip.")
    print(LINE)


def _last_line(traceback_text):
    lines = [ln for ln in traceback_text.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else "(no detail)"


def main():
    caps = preflight()
    print_preflight(caps)

    # Reuse the coverage runner: run the suite under trace, then write coverage.xml.
    # Seed only when no measurement exists (review 2026-09-11, C21): the packaging test reads
    # the artifact while the suite runs, so it must see the previous real measurement, and a
    # crashed run must not leave a placeholder that reads as green.
    if not (PLUGIN_ROOT / "coverage.xml").exists():
        cov.seed_coverage_xml()
    result, counts = cov.run_tests_under_trace()
    tree, line_rate = cov.build_coverage_xml(counts)
    tree.write(PLUGIN_ROOT / "coverage.xml", encoding="utf-8", xml_declaration=True)

    ran = result.testsRun                 # NOTE: testsRun INCLUDES skipped tests
    n_fail = len(result.failures)
    n_err = len(result.errors)
    n_skip = len(result.skipped)
    n_pass = ran - n_fail - n_err - n_skip

    print()
    print(LINE)
    print("RESULTS")
    print(LINE)
    print(f"  DISCOVERED: {ran}")
    print(f"  PASS:       {n_pass}")
    print(f"  FAIL:       {n_fail}")
    print(f"  ERROR:      {n_err}")
    print(f"  SKIP:       {n_skip}")
    print(f"  coverage.xml line-rate: {line_rate:.2%}")

    if n_fail or n_err:
        print()
        print("FAILURES / ERRORS (these must be fixed):")
        for test, tb in list(result.failures) + list(result.errors):
            print(f"  [FAIL] {test.id()}")
            print(f"         {_last_line(tb)}")

    if n_skip:
        print()
        print("SKIPPED TESTS:")
        for test, reason in result.skipped:
            print(f"  [SKIP] {test.id()}")
            print(f"         reason: {reason}")

    print()
    print(LINE)
    unexpected_skip = caps["fully_provisioned"] and n_skip > 0
    if n_fail or n_err:
        print("VERDICT: NOT VERIFIED -- tests FAILED or ERRORED. See above.")
        verdict = 1
    elif unexpected_skip:
        print("VERDICT: NOT VERIFIED -- this machine is fully provisioned, so every")
        print("         test should run, but some SKIPPED. A skip here almost always")
        print("         means a test can't find what it needs (e.g. a moved script),")
        print("         NOT a clean pass. Investigate each SKIP above.")
        verdict = 1
    elif n_skip:
        print("VERDICT: PARTIALLY VERIFIED -- portable host. Each skip above prints its own")
        print("         reason: the live workbooks that corpus.map.json does not resolve here,")
        print("         openpyxl if the preflight shows it missing, or an environment value the")
        print("         export does not ship. Re-run where they resolve to verify those checks.")
        verdict = 0
    else:
        print("VERDICT: VERIFIED -- every discovered test ran and passed; nothing skipped.")
        verdict = 0
    print(LINE)
    return verdict


if __name__ == "__main__":
    sys.exit(main())
