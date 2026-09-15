# Mark-Movement Attribution — {DEAL}, {PERIOD}

> One block per priced tranche. **No mark ships without a "vs. prior, because" sentence.** If you cannot
> write it, dig — that is the signal, not a reason to send. An unexplained move is a stop (step 12).

## {TRANCHE} (e.g. Equity)

| Metric | Prior ({PRIOR_PERIOD}) | Current ({PERIOD}) | Change |
|---|---|---|---|
| Clean price (%) | {prior_px} | {curr_px} | {Δ} |
| Discount margin (bps) | {prior_dm} | {curr_dm} | {Δ} |
| Projected writedown (%) | {prior_wd} | {curr_wd} | {Δ} |
| WAL (yrs) | {prior_wal} | {curr_wal} | {Δ} |

**vs. prior:** {up/down} {magnitude}, driven by {primary factor}, partly {secondary factor}.

**Driver decomposition** (tick the ones that moved; quantify where possible):

- [ ] **Rates** — discount-factor *curve* refresh / accrual / day count. NB: the tranche is a **floater** (coupon resets), so it is largely **insensitive to the benchmark *level*** — this leg is ≈ 0 while the tranche is near par with small projected losses (not for a discounted or heavily written-down tranche). A benchmark move belongs in **Spread**, not here: {note}
- [ ] **Spread** — Spread Analysis DM roll (L32 multiplier → L34); this is the **credit-spread** leg and the usual driver of a market-only move: {benchmark, raw change, dampened adj}
- [ ] **Paydown / amortisation** — Portfolio Maturity Profile balance change: {note}
- [ ] **Credit** — PD / CDR / LGD-severity / SES netting: {note}
- [ ] **Methodology / model** — any change in approach (flag explicitly — most important): {note}
- [ ] **Date / accrual** — val-date roll, accrued, day count: {note}

**Cross-check:** the named drivers reconcile to the total change (sequential or Shapley); residual cross-term is small and noted. If two factors interact materially, report the order-independent (Shapley) split and show the sequential as a check.

---

(repeat per tranche)
