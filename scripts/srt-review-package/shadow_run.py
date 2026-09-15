#!/usr/bin/env python3
"""Shadow-mode harness for the SRT quarterly update (autonomy ladder L-step 1).

READ-ONLY measurement: from a canonical registry + a prior mark + this period's market
inputs, estimate the equity move the way the skill does (RONA-weighted PD/LGD; dampened
DM roll; credit/spread/rate bridge) and diff it against the human's RECORDED ACTUAL mark.
It writes no model and delivers nothing -- its only job is to measure agreement and
stop-correctness so you can trust the pipeline before any write/delivery.

The credit numbers, the tie-out, the dampened DM, and the stop decision are exact and
reproducible. The clean-price number is a TRANSPARENT ESTIMATE for diffing only -- the
penny still comes from Srt dcf.xlsm.

What the estimate simplifies (stated by the 2026-09-11 review; see review/PROPOSALS.md):
  - DM roll: the ADDITIVE form, dm_prior + benchmark_change / divisor. The model's own
    wiring is multiplicative (L34 = L30 x (base + D8/100)) and the two have NOT been
    reconciled -- the units of D8 are unconfirmed. Treat the DM here as the documented
    "bp / 2" rule, not as a reproduction of L34.
  - Credit leg: the writedown is scaled linearly by the expected-loss ratio
    (EL = WA PD x WA LGD). Real tranche loss is capped at detachment and timed; the
    linear form holds only while the tranche is well inside its attachment/detachment.
  - Rate leg: a constant 0. Correct near par with small projected losses; a discounted
    or heavily written-down tranche has a real rate sensitivity that is not estimated.
  - Spread leg: needs `market.spread_duration`; if it is absent the leg is reported as
    "not estimated" and a warning is printed (it is never silently zero).

Usage:
  python shadow_run.py --registry canonical-registry.csv --input shadow-input.json \
      [--stated-notional N] [--report shadow-report.json]
"""
import argparse
import csv
import json


def wavg(rows, field, weight="rona"):
    num = den = 0.0
    miss = []
    for r in rows:
        w = r.get(weight)
        v = r.get(field)
        if w is None:
            continue
        if v is None:
            miss.append(r.get("obligor_id"))
            continue
        num += v * w
        den += w
    return (None if (miss or den == 0) else num / den), den, miss


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", required=True, help="canonical-registry.csv")
    ap.add_argument("--input", required=True, help="shadow-input.json")
    ap.add_argument("--stated-notional", type=float, default=None)
    ap.add_argument("--report", default=None)
    args = ap.parse_args(argv)

    with open(args.registry, newline="", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))
    rows = []
    for r in raw:
        rows.append({"obligor_id": r.get("obligor_id"),
                     "rona": fnum(r.get("rona")), "pd": fnum(r.get("pd")),
                     "recovery": fnum(r.get("recovery")), "lgd": fnum(r.get("lgd")),
                     "status": (r.get("status") or "Performing")})
    perf = [r for r in rows if r["status"] != "Defaulted"]

    with open(args.input, encoding="utf-8") as f:
        inp = json.load(f)
    prior, mkt = inp.get("prior", {}), inp.get("market", {})

    # --- exact, reproducible block ---
    total_rona = sum(r["rona"] for r in rows if r["rona"] is not None)
    perf_rona = sum(r["rona"] for r in perf if r["rona"] is not None)
    wa_pd, _, pd_miss = wavg(perf, "pd")
    wa_lgd, _, lgd_miss = wavg(perf, "lgd")  # lgd already = 1-recovery in canonical

    stop_reasons = []
    stated = args.stated_notional or inp.get("stated_reference_notional")
    if stated:
        gap = abs(total_rona - stated) / stated
        if gap > 0.005:
            stop_reasons.append(f"RONA {total_rona:,.6g} != stated {stated:,.6g} (gap {gap:.2%})")
    if pd_miss:  # review 2026-09-11 (C1/T15): a missing forward PD is a STOP everywhere else
        stop_reasons.append(f"missing PD for {pd_miss}")
    if lgd_miss:
        stop_reasons.append(f"missing recovery/LGD for {lgd_miss}")

    dm_prior = fnum(prior.get("valuation_dm_bps"))
    bench = fnum(mkt.get("benchmark_change_bps"))
    divisor = fnum(mkt.get("dampening_divisor")) or 2.0
    dm_new = (dm_prior + bench / divisor) if (dm_prior is not None and bench is not None) else None

    # --- transparent estimate block (for diffing only) ---
    est = {}
    if None not in (wa_pd, wa_lgd, prior.get("wa_pd"), prior.get("wa_lgd")):
        el_prior = prior["wa_pd"] * prior["wa_lgd"]
        el_new = wa_pd * wa_lgd
        wd_prior = fnum(prior.get("writedown"))
        wd_new = wd_prior * (el_new / el_prior) if (wd_prior and el_prior) else None
        sd = fnum(mkt.get("spread_duration"))
        sd_missing = sd is None  # review 2026-09-11 (C4): never a silent zero
        px_prior = fnum(prior.get("clean_price"))
        spread_leg = (-(dm_new - dm_prior) / 10000.0) * sd * 100 if (dm_new is not None and not sd_missing) else 0.0
        credit_leg = -((wd_new - wd_prior) * 100) if (wd_new is not None and wd_prior is not None) else 0.0
        rate_leg = 0.0  # floater near par: ~0. NOT zero for a discounted / written-down tranche (see docstring)
        px_new = (px_prior + spread_leg + credit_leg + rate_leg) if px_prior is not None else None
        est = {"wa_pd": wa_pd, "wa_lgd": wa_lgd, "el_prior": el_prior, "el_new": el_new,
               "valuation_dm_bps": dm_new, "writedown": wd_new, "clean_price": px_new,
               "bridge_pts": {"credit": round(credit_leg, 3),
                              "spread": ("not estimated" if sd_missing else round(spread_leg, 3)),
                              "rate": rate_leg}}
        if sd_missing:
            print("  WARNING: market.spread_duration is missing -- the spread leg is NOT estimated and the "
                  "clean-price estimate excludes it.")

    # --- agreement vs recorded actual ---
    actual = {k: v for k, v in (inp.get("recorded_actual") or {}).items() if not k.startswith("_")}
    agree = {}
    if actual and est:
        for k, unit in [("clean_price", "pts"), ("valuation_dm_bps", "bps"), ("writedown", "pts")]:
            a, e = fnum(actual.get(k)), est.get(k)
            if a is not None and e is not None:
                d = (e - a) if k != "writedown" else (e - a) * 100
                agree[k] = {"actual": a, "estimate": round(e, 4), "diff_" + unit: round(d, 3)}

    print(f"SHADOW RUN -- {inp.get('deal','?')} {inp.get('period_end','')} ({inp.get('active_tranche','')})")
    print(
        f"  rows {len(rows)} ({len(rows)-len(perf)} defaulted)  "
        f"perf RONA {perf_rona:,.6g}  total RONA {total_rona:,.6g}"
    )
    if wa_pd is not None:
        print(f"  WA PD  {wa_pd:.4%}   (prior {prior.get('wa_pd',0):.4%})")
    if wa_lgd is not None:
        print(f"  WA LGD {wa_lgd:.4%}   (prior {prior.get('wa_lgd',0):.4%})")
    if dm_new is not None:
        print(f"  DM roll: {dm_prior:.0f} {bench:+.0f}/{divisor:g} = {dm_new:.0f} bps (dampened)")
    if est.get("clean_price") is not None:
        b = est["bridge_pts"]
        spread_txt = b["spread"] if isinstance(b["spread"], str) else f"{b['spread']:+.3f}"
        print(f"  EST clean px {est['clean_price']:.3f} (prior {prior.get('clean_price')})  "
              f"bridge: credit {b['credit']:+.3f} / spread {spread_txt} / rate {b['rate']:+.3f}")
        print(f"  EST writedown {est['writedown']:.4%}" if est.get("writedown") else "")
    if agree:
        print("  AGREEMENT vs recorded actual:")
        for k, v in agree.items():
            dk = [x for x in v if x.startswith("diff_")][0]
            print(f"    {k:18s} actual {v['actual']}  est {v['estimate']}  diff {v[dk]:+} {dk.split('_')[1]}")
    if stop_reasons:
        print("  WOULD STOP (escalate, no mark):")
        for s in stop_reasons:
            print(f"    - {s}")
    else:
        print("  No stop conditions in the registry (deterministic checks pass).")
    print("  NOTE: clean-price is a transparent estimate for diffing; the booked number comes from Srt dcf.xlsm.")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump({"deal": inp.get("deal"), "period_end": inp.get("period_end"),
                       "total_rona": total_rona, "perf_rona": perf_rona,
                       "estimate": est, "agreement": agree, "would_stop": stop_reasons}, f, indent=2)
    # shadow mode never "fails" on a stop -- the stop IS the measured signal. Exit 0.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
