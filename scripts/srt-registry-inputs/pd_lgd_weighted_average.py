#!/usr/bin/env python3
"""RONA-weighted PD and LGD from a reference-registry CSV.

Execution helper (NOT skill logic). Standard-library only. Mirrors the registry's
own mechanic:

    WA PD       = SUMPRODUCT(PD, RONA) / SUM(RONA)
    WA recovery = SUMPRODUCT(recovery, RONA) / SUM(RONA)
    WA LGD      = 1 - WA recovery   (or the LGD column directly if recovery is absent)

Built to run on the canonical registry (adapters/canonical-registry-schema.md): it
resolves columns by their EXACT canonical names first (pd / recovery / lgd / rona /
status), and only falls back to fuzzy matching for a raw, un-normalized tape. Rows
whose Status is 'Defaulted' are excluded by default. Missing required values are NOT
filled silently: the tool stops and escalates (exit 1).

Usage:
    python pd_lgd_weighted_average.py <registry.csv> [--include-defaulted]
"""
import argparse
import csv
import sys


def find_col(headers, *needles):
    """First header containing all needle substrings (case-insensitive)."""
    for h in headers:
        hl = h.lower()
        if all(n in hl for n in needles):
            return h
    return None


def resolve(headers, exact, *fuzzy):
    """Prefer an exact canonical column name; else fall back to fuzzy candidates."""
    for h in headers:
        if h.strip().lower() == exact:
            return h
    for cand in fuzzy:
        needles = cand if isinstance(cand, tuple) else (cand,)
        col = find_col(headers, *needles)
        if col:
            return col
    return None


def to_float(s):
    if s is None:
        return None
    s0 = str(s).strip()
    if s0 == "":
        return None
    pct = s0.endswith("%")
    t = s0.replace(",", "").replace("%", "")
    try:
        x = float(t)
    except ValueError:
        return None
    return x / 100.0 if pct else x


def weighted_average(included, total_rona, col):
    """Return (wa, missing_obligors). wa is None if any included row lacks the value."""
    num, missing = 0.0, []
    for row, w, label in included:
        v = to_float(row.get(col))
        if v is None:
            missing.append(label)
        else:
            num += v * w
    return (None if missing else num / total_rona), missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv_path")
    ap.add_argument("--include-defaulted", action="store_true",
                    help="include rows whose Status is 'Defaulted'")
    args = ap.parse_args(argv)

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("ERROR: empty registry", file=sys.stderr)
        return 2

    headers = list(rows[0].keys())
    label_col = resolve(headers, "obligor_id") or resolve(headers, "obligor_name") or headers[0]
    rona_col = resolve(headers, "rona", "rona", ("notional", "amount"), ("reference", "notional"))
    # exact "pd" or probability+default; no bare "pd" substring
    pd_col = resolve(headers, "pd", ("probability", "default"))
    rec_col = resolve(headers, "recovery", "recover")
    lgd_col = resolve(headers, "lgd", "severity")
    status_col = resolve(headers, "status", "status")

    if not rona_col:
        print("ERROR: could not find a RONA / exposure-weight column", file=sys.stderr)
        return 2

    included, excluded, problems = [], [], []
    for i, row in enumerate(rows, start=2):
        label = (row.get(label_col) or f"row {i}").strip()
        if status_col and not args.include_defaulted:
            if (row.get(status_col) or "").strip().lower() == "defaulted":
                excluded.append(label)
                continue
        w = to_float(row.get(rona_col))
        if w is None:
            problems.append(f"{label}: missing RONA")
            continue
        included.append((row, w, label))

    total_rona = sum(w for _, w, _ in included)
    if total_rona <= 0:
        print("ERROR: SUM(RONA) is zero or undefined", file=sys.stderr)
        return 2

    print(f"Registry : {args.csv_path}")
    print(f"Columns  : RONA={rona_col!r}  PD={pd_col!r}  Recovery={rec_col!r}  "
          f"LGD={lgd_col!r}  Status={status_col!r}")
    print(f"Rows     : {len(included)} included, {len(excluded)} excluded (defaulted)")
    print(f"SUM(RONA): {total_rona:,.6g}   <- tie this to the registry's stated total")

    if pd_col:
        wa_pd, miss = weighted_average(included, total_rona, pd_col)
        if wa_pd is None:
            problems.append(f"WA PD blocked: missing PD for {miss}")
        else:
            print(f"WA PD    : {wa_pd:.4%}")
    else:
        # review 2026-09-11 (C10): a registry with no PD column is the LGD-only / defaulted-tab
        # (H11) path, so this is not a STOP -- but it must never read as a computed PD.
        print("WA PD    : NOT COMPUTED -- no PD column in this registry (LGD-only / H11 path). "
              "Not a STOP here; the forward PD must come from elsewhere or the run must stop upstream.")

    # WA LGD: prefer recovery (->1-rec); fall back to an LGD column if recovery is absent/blank.
    wa_lgd, lgd_source = None, None
    if rec_col:
        wa_rec, _ = weighted_average(included, total_rona, rec_col)
        if wa_rec is not None:
            wa_lgd, lgd_source = 1 - wa_rec, "1 - WA recovery"
            print(f"WA recov : {wa_rec:.4%}")
    if wa_lgd is None and lgd_col:
        wa_l, _ = weighted_average(included, total_rona, lgd_col)
        if wa_l is not None:
            wa_lgd, lgd_source = wa_l, "WA LGD column"
    if wa_lgd is not None:
        print(f"WA LGD   : {wa_lgd:.4%}   ({lgd_source})")
    elif rec_col or lgd_col:
        problems.append("WA LGD blocked: need recovery or LGD on every included row")

    if problems:
        print("\nSTOP / escalate (do not fill silently):")
        for p in problems:
            print(f"  - {p}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
