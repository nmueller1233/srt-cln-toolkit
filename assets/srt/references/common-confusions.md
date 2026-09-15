# SRT Common Confusions

Use this reference when the analyst is not asking for the next procedural step,
but is confused about a mechanism that is often handled incorrectly. Give a
longer answer by default. Teach the concept, identify the error pattern, tie it
to the model, and name the evidence needed.

**Contents:** 1. Negative accrued interest during calibration · 2. Pro-rata language vs split-tranche
amortization · 3. EAD vs defaulted notional · 4. CDS coupon / spread / upfront / accrual / settlement ·
5. On-the-run benchmark selection · 6. CDX/iTraxx constituents vs borrower-level CDS · 7. Severity for
newly defaulted and non-liquidated assets.

## 1. Negative Accrued Interest During Calibration

**Short correction:** negative accrued interest is a date/schedule problem, not
a signal to keep goal-seeking `L30`.

In a new-deal calibration the valuation date `D10` is set to the issue date
`D14`, and `L30` is solved so clean price `H36` prints par. The accrual in the
Notes rows is dirty price minus clean price. It is driven by the scheduled
coupon grid, which is anchored by `D18` cashflow start and stepped by `D19`
tenor under the day-count basis in `D22`.

The failure mode is subtle: if `D18` is after `D10`, the model can find a
scheduled accrual-start date that is in the future relative to the valuation
date. The elapsed day-count fraction is then negative, so accrued interest
prints negative. If the analyst keeps solving `L30`, the model is calibrating
the origination DM to a malformed first coupon. That bad anchor then gets
preserved into every later quarterly update.

The mirror case also matters. If `D18` is before issuance, the symptom may be a
spurious positive stub accrual before the note was funded rather than a negative
number. The sign differs, but the fix is the same: do not paper over the date
problem with a different DM.

**Model action:** stop, fix the dates, then re-solve `L30`. Confirm `D10 =
D14`, `D18 <= D10` where appropriate for the model schedule, first coupon date
is not before issuance, and `D22` matches the legal day-count basis. Evidence
should state `D10`, `D14`, `D18`, `D19`, `D22`, the accrual symptom, and the
post-fix clean price target.

## 2. Pro-Rata Language But Split-Tranche Amortization

**Short correction:** do not set `D25` just because the document contains the
phrase "pro-rata." A deal can be pro-rata in one part of the structure and
sequential in another.

The model has one deal-level flag: `D25 ProRata_Amort`. It cannot express
senior notes amortizing sequentially while the junior/residual or equity
position amortizes pro-rata, or a structure where a trigger flips only part of
the stack. If the legal terms contain both a general pro-rata phrase and
per-tranche or trigger-specific sequential mechanics, the general phrase is not
enough to choose the model flag.

The valuation issue is not semantic. Pro-rata paydown keeps leverage closer to
constant. Sequential paydown pays senior tranches first, changes attachment and
detachment over time, starves junior cashflow, and can move residual/equity marks
materially. A single wrong flag can make both the cashflow timing and the credit
enhancement path wrong.

**Model action:** ask for the legal document or approved extraction. Identify
which tranche is being valued, whether the current period is before or after any
trigger breach, and whether the model can represent the legal waterfall. If the
deal is genuinely split, the model has a representation gap with a clean answer:
run the tranches separately or apply an approved workaround, grounded in the
agreement's amortization terms. Do not silently pick `TRUE` or `FALSE`; a
colleague's second look on the chosen workaround is optional, not a gate.

## 3. EAD Versus Defaulted Notional

**Short correction:** the defaulted/non-liquidated loss base is exposure at
default, not necessarily a simple defaulted notional field.

For ordinary funded term loans and bonds, EAD will often equal the outstanding
reference notional or RONA. That is why the shortcut often works. But the
conceptual base is still EAD: the exposure on which the severity will be
applied if the obligor is in default. For revolving or partly undrawn
commitments, EAD may include expected additional drawings, commonly framed as:

```text
EAD = drawn amount + CCF * undrawn commitment
```

Basel materials treat EAD as a core credit-risk component alongside PD and LGD,
and use credit conversion factors for off-balance-sheet commitments. That is the
same conceptual distinction the SRT workflow needs: "reported defaulted
obligation amount" may already be an EAD figure, or it may be only drawn
notional.

**Model action:** read the defaulted/non-liquidated tab and `L5` as the reported
EAD bucket unless the source proves otherwise. Tie the tab to the registry.
If the exposure is a funded bond/term loan, note that EAD equals RONA in the
common case. If the exposure is a revolver, delayed-draw, trade-finance line, or
other commitment, ask whether the reported value is drawn-only or EAD-adjusted
and what CCF was used. Do not overwrite a reported EAD with a pure notional
shortcut.

## 4. CDS Coupon, Spread, Upfront, Accrual, And Settlement

**Short correction:** the CDS coupon is not always the current market spread.
Modern standard CDS trades often use a fixed coupon plus an upfront payment to
make the trade economic at current spreads.

The intuition is insurance. The protection buyer pays a running premium to the
protection seller. In a standardized CDS or CDS index, that running coupon is
fixed by convention for the contract, while the market spread changes every day.
The difference is handled through upfront value. If the market spread is above
the fixed coupon, the protection buyer is receiving underpriced running
protection and typically pays upfront. If the market spread is below the fixed
coupon, the buyer is agreeing to overpay on the running coupon and typically
receives upfront.

The trade also has clean-price and accrual mechanics. CDS index documentation
describes fixed coupons paid quarterly, upfront or unwind payments at initiation
or close, and clean quotation conventions. Accrued coupon is handled separately
so all protection buyers pay the same coupon on the payment date.

Credit-event settlement is another common source of confusion. When a credit
event occurs, settlement can involve physical settlement or auction/cash
settlement depending on the contract. In auction settlement, the auction final
price functions as a market-implied recovery for the deliverable obligations.
For an index, a constituent credit event can lead to a new index version with the
defaulted entity at zero weight and index notional reduced by that constituent
weight after the auction process.

**Model action:** for the SRT DCF, keep the distinction between contractual
coupon/margin, origination DM `L30`, valuation-date DM `L34`, and CDS/index
spread evidence. CDS spread evidence supports the spread-change lane; it is not
a reason to re-solve `L30` in a quarterly update. If an actual trade prints on
the SRT tranche, that is different: it may support a multiplier-base review, but
it needs evidence and reviewer approval.

## 5. On-The-Run Benchmark Selection

**Short correction:** use the current on-the-run series for benchmark evidence
unless the deal's approved methodology says otherwise. Do not use a stale
off-the-run series just because it is familiar.

CDX and iTraxx series roll every six months, typically in March and September.
At each roll, a new series is created with updated constituents. Older series
can keep trading, but liquidity concentrates in the latest on-the-run series,
and S&P DJI notes that the 5-year tenor is typically the most liquid point. That
is the theoretical reason the current on-the-run series is usually the best
market evidence: it is where current risk transfer, dealer liquidity, and
transparent pricing concentrate.

Selection still needs to match the deal. A USD North American pool points toward
the CDX.NA family. A European pool points toward iTraxx Europe. Broadly
investment-grade exposure points toward CDX.NA.IG or iTraxx Europe Main;
sub-investment-grade exposure points toward CDX.NA.HY or iTraxx Crossover.
Financial-heavy European pools may require Senior Financials or Sub Financials
instead of Main. Tenor should match remaining term or WAL as closely as the
available market allows, with a note when the liquid tenor and model tenor
differ.

**Example:** a USD pool with mostly BB/B leveraged borrowers and a 3-year
remaining term might use a CDX.NA.HY on-the-run series, then document why a 5Y
market quote was interpolated, adjusted, or accepted as the best liquid proxy
for a 3Y model input. A EUR investment-grade corporate pool would more naturally
start with iTraxx Europe Main; a EUR high-yield pool starts with iTraxx
Crossover.

**Model action:** for new-deal setup, surface benchmark selection first because
it anchors future spread evidence. For a quarterly update, keep the previously
approved benchmark unless pool quality, region, sector, WAL, or methodology
changed enough to require review. Evidence should include series, version,
tenor, currency/region, prior/current spread, roll date awareness, and why the
benchmark fits the reference portfolio.

## 6. CDX/iTraxx Constituents And Borrower-Level CDS

**Short correction:** an index spread is a market-wide benchmark, not a direct
spread for each borrower in the reference pool. A single-name CDS is useful only
when the reference entity and contract terms actually match the risk being
proxied.

CDX and iTraxx are portfolios of CDS reference entities. S&P DJI describes CDX
as covering North America and emerging markets, while iTraxx covers European,
Asian, and emerging market tradable CDS indices. iTraxx Europe Main has 125
equally weighted European names; iTraxx Crossover has 75 liquid sub-investment
grade entities. The index is useful because it is liquid and standardized, but
that liquidity comes from broad representation, not borrower-specific precision.

Borrower-level or obligor-level CDS is different. It can be a strong proxy when
the SRT reference pool has a dominant obligor, an originator/counterparty CDS is
part of the approved methodology, or the borrower itself has a liquid CDS
contract matching legal entity, seniority, restructuring clause, currency, and
tenor. It is a poor proxy when the borrower has no liquid CDS, the quoted entity
is the wrong parent/subsidiary, the contract references the wrong seniority or
restructuring convention, or the obligor is not representative of the pool.

There is also index basis. Index spreads can differ from the weighted fair value
of the constituents because of liquidity, tenor mismatch, demand for index
protection, and single-name market frictions. That is not a defect; it is why
the index is a benchmark rather than a literal weighted-average borrower spread.

**Model action:** use index evidence for broad market spread movement and
single-name evidence only when the approved process and the legal/entity match
support it. If using a single-name CDS, document legal entity, RED/RIC or vendor
identifier, seniority, doc clause, tenor, currency, source, and why it maps to
the SRT risk. If the borrower-specific CDS and the index diverge materially,
explain the divergence rather than averaging blindly.

## 7. Severity For Newly Defaulted And Non-Liquidated Assets

**Short correction:** a newly defaulted name is usually estimated severity
`H11`, not realised severity `H10`, until the loss is finally determined.

Defaulted/non-liquidated assets are no longer part of the forward-performing
pool for PD/LGD. They cannot default again, so keeping them in forward PD
double-counts. But they usually remain in the notional/EAD tie-out until they
are written down or liquidated, so dropping them from the registry total also
breaks the model. The name moves out of forward-performing assumptions and into
the defaulted/non-liquidated loss bucket.

The severity hierarchy is contract-first:

1. If the deal or CDS terms define a fixed recovery or loss-determination
   method, use that unless approved borrower-level insight overrides it.
2. If no contractual figure governs, use current credit research such as
   Debtwire to understand the event, restructuring path, assets, sponsor
   support, legal process, and expected recovery direction.
3. Anchor the number with the secondary price of the most comparable debt
   instrument, matched by issuer, seniority, lien/security, sector, currency,
   and tenor. Treat price as market-implied recovery and severity as
   `1 - recovery`.
4. RONA/EAD-weight the per-name recoveries across the defaulted/non-liquidated
   bucket.

Do not equal-weight defaulted names. Do not use a subordinated bond price for a
senior secured reference obligation without explaining the mismatch. Do not use
`40` when the script expects `0.40` or `40%`. Do not overwrite a crystallized
realised loss on `L4` / `H10` with a refreshed estimate.

**Model action:** calculate one `H11` estimated severity for the
defaulted/non-liquidated bucket, tied to the reported EAD and re-marked each
period. Once recovery is finally determined, move the treatment to realised
loss (`L4` / `H10`) according to the deal process. For newly defaulted and
non-liquidated names without a contractual severity, go to the secondary price of
the most comparable bond first, then the S&P Global risk gauge; give the factors
and a recommendation. The mark depends on an estimated recovery, so a colleague's
second look is reasonable on a thin or illiquid comp.

## Additions

When another recurring confusion appears, add it here only if it is genuinely
tricky, nuanced, or often wrong. Ordinary checklist steps belong in the lane
skills, not in this common-confusions skill.

## Source Anchors

Internal plugin references:
- `spreads-dm-calibration.md`
- `benchmark-spread-pulling.md`
- `credit-risk-parameter-theory.md`
- `defaulted-and-nonliquidated-borrowers.md`
- `srt-waterfall-and-triggers.md`
- `pd-lgd-severity.md`
- `model-cell-map.md`

External grounding used for theory:
- S&P DJI, CDS Indices Primer and CDX/iTraxx product pages: index rolls,
  on-the-run liquidity, index constituents, fixed coupon, upfront, accrual, and
  credit-event index version mechanics.
- ISDA / CDS Standard Model materials: fixed-coupon plus upfront standard CDS
  conversion and credit-event settlement conventions.
- Basel Committee, Basel III final reforms: EAD, CCF, and off-balance-sheet
  commitment conversion concepts.
