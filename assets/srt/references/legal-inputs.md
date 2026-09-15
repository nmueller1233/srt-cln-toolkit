# Legal Inputs → Model (Source-Only)

**Read for new-deal setup or a legal amendment.** This lane is **manual and human-reviewed** — it is
*not* automated in the pilot. The skill documents the fields and the evidence; a human extracts and
approves before any contractual value enters the model. (Routine quarterly updates skip this lane entirely.)

Two source docs (in the corpus): the **extraction prompt** (pulls ~48 modelling fields from the CLN
indenture / CDS confirmation / offering memo) and the **legal-to-model mapping** (where each lands on the
`Inputs` tab). Full field list and page-cited values come from running the extraction prompt; below is
the load-bearing field→cell map plus the nuances that bite.

## Field → Inputs cell (the ones with a cell)

| Legal field | Cell | Note |
|---|---|---|
| Issue / closing date | `D14` | Origination anchor; **not** the valuation date (`D10`). |
| Maturity / scheduled termination | `D12` | `E12` carries a "First Call Date" note. |
| First call date | `D12` | Extract **separately** from legal final maturity even though both map to `D12`. |
| Reinvestment / replenishment end | `D17` | Watch terminology: Replenishment / Revolving / **Exclusion Date**. |
| Start of cash flows | `D18` | First-funding/cashflow anchor. |
| Payment frequency | `D19` | `3` = quarterly, `1` = monthly. |
| CDS termination period | `D26` | Extension/workout/final-settlement tail. |
| Issue price | `D16` | Par = `1`. |
| Currency | `D27` | Drives the fixing source (SOFR vs EURIBOR). |
| Day-count basis | `D22` | `0`=30/360, `1`=ACT/365, `2`=ACT/360. |
| Pay at EOM | `D20` | TRUE/FALSE. |
| Reference rate | `D21` | Cell holds the current rate; label confirms the benchmark. |
| Notional basis for interest | `H3` | Coupon on **original vs outstanding** notional — determine explicitly. |
| Severity (liquidated) | `H10` | Decimal. |
| Severity (defaulted, not liquidated) | `H11` | Decimal; distinct from `H10`. |
| Recovery lag | `H12` | **Periods**, not days. |
| Payment lag | `H4` | Business **days**. |
| Tranche names (senior→sub) | `G16:G20` | Row 16 senior → row 20 equity. |
| Floating-rate? per tranche | `H16:H20` | TRUE/FALSE. |
| Contractual margin per tranche | `I16:I20` | **Decimal — 725bps = 0.0725.** |
| Original balance per tranche | `J16:J20` | Preserve full notionals. |
| Original portfolio balance | `L3` | Total reference notional. |

## Fields with no Inputs cell (narrative / waterfall — capture in notes)

- **Amortisation type** (pro rata vs sequential → `D25`) and **amortisation triggers** (cum default %,
  delinquency %, OC test, failure-to-pay, coverage breach) — list each; pro rata with a sequential
  trigger on breach is common.
- **Synthetic excess spread** (fields 26 & 47) — mechanism only; see `ses.md`.
- **Funded vs unfunded**, eligible collateral/haircuts, clean-up call (~10%), optional redemption,
  substitution mechanics, reserve account, credit-event definitions, reg-capital treatment
  (SEC-IRBA / SEC-SA / STS), step-up margin, replenishment quality tests, servicer.
- **Parties, collateral characteristics, WAL/WAM** — narrative (WAL appears only as a model *result*).

## Nuances that bite

- **Three maturities are distinct:** legal final maturity, first call date, and the model maturity
  (`D13 = D12`). Capture call date and legal final separately.
- **bps → decimal** for margins (`I`-col) and DM (`L`-col). But some *results* are already in bps
  (Origination DM `L30`, Valuation DM `L34`) — don't double-convert.
- **Severity split** (`H10` liquidated vs `H11` not-yet-liquidated) and **lag units** (`H12` periods vs
  `H4` days) — easy to swap.
- **Never fabricate.** If a field isn't in the doc, say "Not found"; flag ambiguity with **both
  readings**; use the document's exact terminology in parentheses.

## Workflow (how the extraction is run)

One document per pass: extract from the **primary** doc first, then upload supplementals and ask only to
**fill gaps**. The prompt is **reusable unchanged for quarterly revaluations** — only the uploaded doc
and deal name change. Output = a numbered field list (value + page) plus a five-paragraph deal summary.

## Not legal fields — set each quarter from the tape/analyst (don't re-pull from legal)

`D10` Valuation Date · `D11` Last Portfolio Update · `D21` SOFR fixing · `L4`/`L5`/`L7` realised /
defaulted-not-liquidated / repaid balances · `H7`/`H9`/`H10` CDR/CPR/severity assumptions.
