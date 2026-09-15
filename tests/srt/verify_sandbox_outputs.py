#!/usr/bin/env python3
"""Verify sandbox agent scenario writeups.

This is intentionally stricter than Plugin Eval's "scenario completed" status:
the scenario only passes if the generated markdown contains the required SRT
decisions and control language.
"""
import re
import sys
from pathlib import Path


CHECKS = {
    "ses-hardcoded-default": [
        ("ses recomputation", [r"recomput", r"ses"]),
        ("do not reuse hardcoded prior value", [r"hardcod", r"(do not|not|never|replace|recomput)"]),
        ("new defaulted obligation named or treated", [r"(new )?default", r"(obligation|carpathia|name)"]),
        ("gross loss calculated", [r"gross loss", r"12(\.0|\.00| mm|mm)?"]),
        ("ses available calculated", [r"9\.3|9\.31875|available ses"]),
        ("residual tranche loss calculated", [r"2\.68|2\.68125|residual"]),
        ("ses netted before tranche allocation", [r"net", r"ses", r"(before|first)", r"tranche"]),
        ("default excluded from performing pool", [r"(exclude|remove)", r"(performing|forward)"]),
        ("human review only", [r"human", r"review"]),
    ],
    "new-deal": [
        ("classified new deal", [r"new[-_ ]deal|new deal"]),
        ("not a roll-forward", [r"not .*roll|no .*roll|do not .*roll"]),
        ("legal source only / human review", [r"legal", r"(source|manual)", r"human|review"]),
        ("origination dm calibration once", [r"origination", r"dm", r"(once|one-time|one time)"]),
        ("calibration to par", [r"(par|clean price)", r"(goal seek|calibrat|target)"]),
        ("margins decimal", [r"decimal|0\.0900|0\.09|0\.045|0\.011"]),
    ],
    "lgd-only-registry": [
        ("rona ties", [r"rona", r"(tie|ties|reconcile|1000|1,000)"]),
        ("lgd can be used", [r"lgd", r"(use|available|mapped)"]),
        ("pd missing", [r"pd", r"missing"]),
        ("do not fabricate pd", [r"(do not|not|never)", r"(fabricate|invent|infer|impute)", r"pd"]),
        (
            "stop or analyst fallback",
            [r"(stop|block|quarantine|exception|fallback)", r"(analyst|approved|approval|pd)"],
        ),
        ("not model-ready mark", [r"(not|no|block|stop)", r"(model-ready|model ready|mark|output)"]),
    ],
    "sequential-trigger": [
        ("trigger occurred", [r"trigger", r"(occurred|active|tripped|triggered)"]),
        ("do not continue pro rata", [r"(do not|not|never)", r"pro[- ]?rata|pro[- ]?rata.*silently"]),
        ("sequential waterfall", [r"sequential", r"waterfall|payment"]),
        ("human review or stop", [r"(human|manual)", r"review|stop"]),
        ("trigger attribution", [r"trigger", r"attribution|because|driver|reason"]),
    ],
}


def contains_all(text, patterns):
    return all(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in patterns)


def verify_file(path):
    scenario_id = path.stem
    text = path.read_text(encoding="utf-8")
    checks = CHECKS.get(scenario_id)
    if not checks:
        return [f"{path.name}: unknown scenario id"]
    failures = []
    for label, patterns in checks:
        if not contains_all(text, patterns):
            failures.append(f"{path.name}: missing {label}")
    if re.search(r"could not .*inspect|could not .*read|access failed|shell.*failed|not exposed", text, re.I):
        failures.append(f"{path.name}: output admits it did not inspect scenario/plugin inputs")
    return failures


def main(argv=None):
    root = Path(argv[0]) if argv else Path("sandbox-output")
    if root.is_file():
        files = [root]
    else:
        files = sorted(root.glob("*.md"))
    if not files:
        print(f"ERROR: no sandbox output markdown files found under {root}", file=sys.stderr)
        return 2
    failures = []
    for path in files:
        failures.extend(verify_file(path))
    if failures:
        print("Sandbox output verification failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(f"Sandbox output verification passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
