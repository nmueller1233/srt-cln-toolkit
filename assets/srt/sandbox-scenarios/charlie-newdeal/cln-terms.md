# Charlie SRT — synthetic CLN term sheet (new-deal setup)

A synthetic term sheet standing in for the legal docs an analyst would extract from. **Run type:
new-deal setup.** Valuing the **Equity** tranche.

## Deal & dates

| Term | Value |
|---|---|
| Deal name | Charlie SRT 2026 |
| Currency | USD |
| Issue / closing date | 2026-05-15 |
| Start of cash flows (first funding) | 2026-05-21 |
| First call date | 2031-05-21 |
| Legal final maturity | 2034-05-21 |
| Reinvestment period end | 2029-05-21 |
| Payment frequency | Quarterly |
| Day-count basis | ACT/360 |
| Pay at end of month | No (pays on the 21st) |
| Reference rate | Daily SOFR |
| Issue price | Par (100) |

## Capital structure (USD mm; total reference pool 2,000)

| Tranche | Attach–Detach | Original balance | Coupon |
|---|---|---|---|
| Senior | 8%–100% | 1,840 | SOFR + 1.10% |
| Mezzanine | 3%–8% | 100 | SOFR + 4.50% |
| Equity (first-loss) | 0%–3% | 60 | SOFR + 9.00% |

## Other terms

- Amortisation: **pro rata**, with a sequential trigger on a 5% cumulative-default breach.
- **Synthetic excess spread:** 0.50%/yr, use-it-or-lose-it.
- Clean-up call at 10% of the original pool. Reg-capital treatment: SEC-SA.
- **Active tranche to value:** Equity.

*(No model mapping is provided — map the fields to the model and calibrate per the standard process.)*
