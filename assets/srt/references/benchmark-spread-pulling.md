# Benchmark Spread Pulling & the Spread-Analysis Roll

> **GUIDANCE — process + general market-data theory.** How to source CDS / CDX / iTraxx spread inputs that drive the
> quarterly DM roll on `Srt dcf.xlsm`, which benchmark to pick, and why the adjustment is built the way it
> is. The **binding** wiring is the model's `Spread Analysis` tab and `spreads-dm-calibration.md`; this file
> does not override them. Exact add-in mnemonics/RICs and any deal-specific benchmark choice must be
> **confirmed in the add-in's formula builder and with a colleague** before a live mark. Local data access is not
> the same as work entitlement — only pull what the run's permissions allow.

**Contents:** model wiring (`Spread Analysis`) → three pull routes (CapIQ / Refinitiv /
connectors) → instruction set (§1 monthly refresh · §2 on-the-run index pick · §3
single-issuer CDS · §4 adjustment theory) → the multiplier (what / how / why) → gates &
evidence → sources. Jump to the section you need; this file isn't meant to be read end-to-end.

## What the model actually does (read this first)

The `Spread Analysis` tab is a tiny, two-benchmark engine (verified wiring):

| Cell | Content | Meaning |
|---|---|---|
| `A1` | `IQT########` · `B1="CDS 3 Year"` · `D1=[2]Inputs!E13` | CapIQ identifier + tenor; `D1` links remaining term |
| `A2` | `US` · `B2`/`C2` = period start / end dates | the month the pull covers |
| `B3:D3` | `Prior Month` · `Current Month` · `1 Month Change` | the three columns |
| `A4` | **`CDX`** — `B4`=prior, `C4`=current, `D4 = C4−B4` | the **on-the-run index** benchmark |
| `A5` | **originator single-name CDS** — `B5`/`C5`/`D5=C5−B5` | a **single-issuer** CDS (originator/counterparty) |
| `D7` | `=AVERAGE(D4:D5)` | the **aggregate** 1-month change (index + single-name) |
| `D8` | `=D7/2` | the **÷2-dampened** aggregate change |

`D8` feeds the multiplier `L32 = 96.1975% + 'Spread Analysis'!D8/100`, and `L34 = L30 × L32` is the
valuation-date DM (`M34 = L34/10000`). So: **two benchmarks → average their monthly change → halve it →
nudge the multiplier → scale the origination DM.** (`spreads-dm-calibration.md`, `model-cell-map.md`.)

## Three ways to pull the spreads

The model is fed by an **Excel add-in** today (the `IQT…` identifier and the `[2]` external link are CapIQ).
Pick the route your desk is entitled to; **record the source, identifier, date, and value** every time.

### 1. S&P Capital IQ Excel add-in (the current method)
- The `CIQ` function pulls a data item for an identifier, optionally as a time series:
  `=CIQ("<identifier>", "<mnemonic>", "<date or period>")`. The tab's `A1` (`IQT########`) is a CapIQ
  CDS time-series identifier; `B1` records the tenor ("CDS 3 Year").
- For CDS, use the **CDS pricing template / `IQ_CDS_LIST`** to find the entity's CDS series, then pull the
  spread time series. **Confirm the exact CDS-spread mnemonic in the Formula Builder** — the cheat sheets
  list `IQ_CDS_LIST` but not a single canonical spread mnemonic, so verify against the live add-in rather
  than hard-coding one.
- Match the **tenor** to the model cell (here 3-year) and the **currency/region** (`A2="US"`).

### 2. LSEG / Refinitiv Workspace (ex-Eikon) Excel add-in
- Use **Build Formula** (the Refinitiv/LSEG tab) → enter the CDS instrument → add fields. Patterns:
  `=@TR("<RIC>","TR.CDSParMidSpread","SDate=<start> EDate=<end> Frq=M")` for a history, or `=RHistory(...)`.
- **CDS RIC nomenclature** is found in the *CDS / Single Quote* app, e.g. a 5-year senior USD single-name
  looks like `<ENTITY>5YUSAX=MP` (entity-tenor-currency-docclause-source). Useful spread fields:
  `TR.PARMIDSPREAD` / `MID_SPREAD` (mid), plus bid/ask variants. **Confirm the RIC in the CDS Quote app**
  before trusting it.
- **RDP-function syntax (proven pattern — the Rates Engine workbook uses exactly this wiring):**
  as-of pulls
  `=RDP.HistoricalPricing(<RIC or range>,"<FIELD>","START:"&ValDate&" END:"&ValDate&" INTERVAL:P1D",," Transpose:Y",<anchor>)`
  return a field (e.g. `MID_SPREAD`) for a list of RICs on the valuation date (driver cell + spill
  anchor). Chain expansion `=RDP.Data("<0#chain>","","CH=Fd RH=IN",<anchor>)` works for **rate
  curves** — but **NOT for CDS index constituents** (verified: no working `0#` CDS chains exist);
  index constituents come from `TR.CDSConst*` fields on the plain index RIC, then the
  CUSIP → `TR.CDSPrimaryCDSRic` bridge for per-name quotes. Generic on-the-run RICs (verified):
  `ITEEU5Y=MP` (Main), `ITEXO5Y=MP` (Crossover), `CDXIG5Y=MP`, `CDXHY5Y=MP` (**price** terms,
  field `MID_PRICE` — always pass the field explicitly). Stored form in the file is `_xll.RDP.*`;
  references in the author's environment (not shipped): a rates workbook that uses the same idiom for OIS
  curves, and an agent reference pack with the full RIC tables, confidence flags and source URLs.

#### Standing requirement — 5Y on-the-run CDX & iTraxx tracking (added 2026-07)
In addition to the deal-tenor-matched leg in `Spread Analysis` (3Y in the live file), the desk tracks
**CDX and iTraxx at the 5-year on-the-run liquid tenor** every period — the 5Y point is the liquidity
benchmark of the CDS index market and the cleanest cross-deal read. Standing set: **iTraxx Europe Main,
iTraxx Crossover (HY), iTraxx Sub Financials 5Y** (EUR side) and **CDX.NA.IG / CDX.NA.HY 5Y** (USD side),
plus the **constituents of the current on-the-run 5Y iTraxx** for dispersion/skew exhibits. This lives in
the **Benchmark & Correlation tracker workbook**, which is maintained outside this repository, not in
`Srt dcf.xlsm` — the tracker prepares, a human keys the model. Two disciplines:
- **Roll consistency:** the indices roll every March 20 / September 20. A period change that spans a roll
  must be computed on a **constant series** (keep the old-series RIC through roll quarters) or the
  composition jump contaminates the DM roll — Q1 and Q3 marks are the exposed ones.
- **Quoting units:** iTraxx and CDX.IG quote in **spread (bps)**; **CDX.NA.HY quotes in price terms** —
  never mix the two in one change column.

### 3. Codex / ChatGPT (LSEG & S&P) connector plugins — cross-check only
- This platform exposes LSEG (`lseg:*`) and S&P Capital IQ (`sp-global:*`) connectors that can fetch market
  data. Treat them as a **grounding / cross-check** layer, **not the system of record**: the model's add-in
  pull stays the source of truth, and any connector pull is **subject to the run's data-permission/entitlement
  gate**. If a connector value and the add-in value disagree, that is a STOP to investigate, not a silent
  override.

## Instruction set

### 1) Replicate the current benchmarks with updated data (this month vs. last month)

The monthly refresh is a **column shift + a fresh pull**, not a re-pick of the benchmark:

1. **Move `Current Month` → `Prior Month`:** for each benchmark row, set `B = ` last period's `C` value
   (`B4`, `B5`). Keep the same benchmarks (`A4=CDX`, `A5=<single-name>`) unless a new-deal review changed
   them (see §2/§3).
2. **Pull this month's value** into `Current Month` (`C4`, `C5`) for the **same identifier and tenor**, at
   the valuation-date convention (month-end label, last available business-day close — `dates-rates-daycount.md`).
3. **Update the period dates** `A2`/`B2`/`C2` to the new month.
4. **Leave the formulas alone:** `D4=C4−B4`, `D5=C5−B5`, `D7=AVERAGE(D4:D5)`, `D8=D7/2` recompute.
5. **Leave the multiplier base alone.** `L32 = base + D8/100`. The base (`96.1975%`) is **set once when the
   deal is onboarded** (see "The multiplier" below) and is **not** a benchmark output — a routine monthly
   quarterly update changes only the spreads, so only `D8/100` moves. Do **not** touch the base on a quarterly update
   (the one exception is a trade printing on the deal — the rare example below).
6. **Evidence:** source + identifier + tenor + both spreads + the raw change, the dampened `D8`, and the
   before/after multiplier and DM (`L32`/`L34`). A reviewer must reproduce `L34` from the saved inputs.

### 2) Pick the on-the-run CDS *index* for the deal (side note always; FIRST thing for a new deal)

The index is the broad-market leg. **On-the-run = the current active series** (CDX/iTraxx roll every
**March 20 / September 20**; always benchmark to the live series, not a stale one). Choose by deal
characteristics and the reference portfolio:

- **Currency / region:** USD pool → **CDX.NA** family; EUR pool → **iTraxx Europe** family. (`A2` records region.)
- **Credit quality of the reference pool:** broadly IG → **CDX.NA.IG** / **iTraxx Europe Main**; sub-IG /
  leveraged → **CDX.NA.HY** / **iTraxx Crossover**.
- **Sector concentration:** a bank/financials-heavy reference set → **iTraxx Senior/Sub Financials**;
  otherwise the main corporate index.
- **Tenor:** match the index tenor to the deal's **remaining term / WAL** (the model uses 3-year here; the
  5-year is the most liquid point — 3/5/7/10y trade, SenFin/SubFin only 5/10y).

For a **new deal this is the first item to surface** (the benchmark choice anchors the whole roll); for an
existing deal, **surface it as a side note** each quarter to confirm the original choice still fits (the
pool's quality/sector/WAL drift over time, and the series rolls).

### 3) Find the single-issuer CDS

The single-name leg ties the mark to the **specific reference entity** — typically the **originator /
protection counterparty** (here the originator), or a dominant reference obligor. To select it:

- **Entity:** the correct legal issuing entity (e.g. the originator's top-level legal entity, not a subsidiary).
- **Seniority & doc clause:** senior vs. subordinated, and the restructuring clause must match how the
  series is quoted (the RIC/identifier encodes this).
- **Tenor & currency:** match the model cell tenor (3-year here) and the deal currency.
- **Formulas:** CapIQ `=CIQ("<entity CDS identifier>","<spread mnemonic>","<date>")` (find the identifier
  via `IQ_CDS_LIST` / the CDS template); Refinitiv `=@TR("<entity>5YUSAX=MP","TR.PARMIDSPREAD",...)`.
  **Verify the identifier/RIC and tenor in the add-in before use.**

### 4) Benchmark-spread-adjustment theory (how it relates to coupon size, and the multiplier)

**Why a benchmark adjustment at all.** The tranche is calibrated **once at origination** — the
**Origination DM (`L30`)** is solved so the tranche prices to par on day one and records its risk profile
(`spreads-dm-calibration.md`). After that, we do **not** re-underwrite the credit each quarter; we let the
**market** move the mark by tracking how a relevant **credit-spread benchmark** has moved and applying a
**proportional** adjustment via the multiplier. This is the standard fair-value approach for a position
whose primary risk is **credit spread**, not rates.

**It's a floater — the move is a spread move, not a rates move.** The coupon resets to SOFR/EURIBOR, so the
price is largely insensitive to the **benchmark *level***; what re-prices the tranche is the change in the
**discount margin** (the credit-spread leg). So the benchmark we track is a **CDS** measure (index +
single-name), and a benchmark move books under **spread**, not rates (`spreads-dm-calibration.md`,
`srt-waterfall-and-triggers.md`).

**The multiplier (what/how/why is its own section below).** Rather than re-solving `L30`, the model scales
it: `L34 (val-date DM) = L30 × L32`. See "The multiplier: what it is, how it's derived, why it's used"
below for the full treatment; in brief, it is **proportional** (a % of the tranche's own DM), so a tranche
that originated wide moves more in absolute bps for the same benchmark move than a tight one.

**Relation to coupon size.** Two linked effects:
- **Dampening scales with coupon size and benchmark volatility.** A single month's CDS print is noisy, so
  the change is **muted** (here ÷2 of the average). A thin, **high-coupon** first-loss/equity piece against
  a noisy benchmark warrants **more** muting than a tight senior — the midpoint DM should not chase one
  noisy print (`spreads-dm-calibration.md`). Record the factor and its rationale each period.
- **Price impact ≈ −(spread duration) × ΔDM.** For a floater, spread duration ≈ WAL, so the *same* ΔDM
  moves a longer-WAL tranche more. And because the multiplier is proportional, a larger origination
  DM/coupon produces a larger absolute ΔDM (`L30 × ΔL32`) for the same benchmark move — so **coupon/DM
  size amplifies the absolute mark move**, while the floating coupon keeps the **rates** leg ≈ 0.

**Aggregation of the two benchmarks.** The model averages an **index** change and a **single-name** change
(`D7`), then dampens (`D8`). The index captures broad market credit; the single-name captures the
originator/counterparty's idiosyncratic spread. Averaging blends systematic and name-specific moves; if the
two **diverge materially** in a period, that divergence is worth a note (it can signal an
idiosyncratic event that the blended number masks).

## The multiplier: what it is, how it's derived, why it's used

**What it is.** `L32` is a single scalar that turns the **origination DM** into the **valuation-date DM**:
`L34 (val-date DM) = L30 (origination DM) × L32`. It has two parts — a **base** (`96.1975%` in the live
file) plus the **current month's dampened benchmark change** (`+ D8/100`).

**Why it's used.** The tranche's primary risk is **credit spread**, not rates (it's a floater — see §4).
The multiplier lets the desk mark the position to where its spread sits **without re-underwriting the
credit** every period: scale the origination anchor by how the market has moved. It is **proportional** (a
% of the tranche's own DM), so a tranche that originated wide moves more in absolute bps than a tight one
for the same market move — the economically sensible behaviour, and why a multiplier is used rather than an
additive bp bump.

**How it's derived — a key step when setting up a NEW deal.** When a deal is first built into the model,
derive the base right after solving the origination DM (`spreads-dm-calibration.md`, new-deal calibration):

1. **Solve `L30`** so the tranche prices to par at issue (the origination anchor).
2. **Derive the base:** set `L32`'s base so the model **clean price `H36` equals where the tranche actually
   prices given current market levels**, judged from **comparable new-issue spreads / coupons** on the same
   shelf. The model keeps these comps next to the multiplier for exactly this — live: `N32`/`N33` hold recent comparable new-issue
   coupons on the same shelf (e.g. 8.25% then 7.50% on successive prints, compressing). Practically, Goal
   Seek `L32` (with the month's `D8`) so `H36` = the market price implied by the comps, and read off the base.
3. **Record the comparables and the target price used**, so the base is reproducible (see evidence).

Worked read of the live file: `L30 = 553.45 bps`, base `96.1975%` → ~`532 bps`, `L34 = 539.8 bps`,
`H36 ≈ 100.01`. The comps compressing (8.25% → 7.50%) is why the deal prices tighter than origination, the
base sits **below 100%**, and the mark is **just above par**.

**How it behaves on a quarterly update.** The base is **held fixed**; only the monthly benchmark change `D8`
moves the multiplier (§1). Do **not** re-derive the base each quarter — that would re-state the mark for a
methodology reason rather than a market one. (`L30 × [ fixed base + this-month `D8/100` ]`.)

**Why "related to the coupon" (the FRN price↔margin link).** A floater prices off the gap between its
**quoted margin** (the contractual coupon spread) and the **required margin** (the DM):
required DM **=** quoted margin → price **= par**; **<** → **premium** (>par); **>** → **discount** (<par).
The coupon level is the anchor of the price↔DM map, and price sensitivity to a DM move ≈ spread duration
(≈ WAL) — so deriving the base from a target price runs **through the coupon**.

**Example scenario (uncommon): a trade prints on the deal.** Secondary trades are rare, but a trade is the
cleanest possible market input. If one occurs, derive the base the same way — Goal-Seek `L32` so `H36` =
the **trade price** instead of the comp-implied price — and note the trade. This is the one case where the
base changes on an otherwise routine quarterly update.

**Process note (reproducibility).** The base is a hard-keyed constant — a reviewer can't reproduce it
unless its basis is recorded. Whenever it is set, capture the comparables (or trade) used, the target
price, and the goal-seek result. (Confirm with the model owner whether the base ever absorbs prior
months' `D8` between deals/trades, or stays fixed until the next new-deal setup / trade — the single-month
`D8 = C−B` wiring suggests it stays fixed.)

## Gates & evidence

- **Stop** if the benchmark selection is unclear, the on-the-run series/tenor doesn't fit the deal, the
  add-in source is unavailable/unverified, or a connector cross-check disagrees with the add-in.
- **Evidence every period:** source + identifier/RIC + tenor + currency; prior/current spreads for **both**
  legs; the raw change, the dampening factor and rationale; and the before/after multiplier and DM bridge.
  For a **new deal**, additionally record the **index-selection rationale**, the **single-name choice**, and
  the **multiplier-base derivation** (comparables used + the target price the base was set to).

## Sources (external grounding — not deal rules)

- Capital IQ Excel plug-in / `CIQ` function, `IQ_CDS_LIST` and CDS pricing templates: S&P Capital IQ Excel
  Plug-in manuals & cheat sheets (capitaliq.com; spglobal Market Intelligence).
- LSEG/Refinitiv Workspace Excel **Build Formula**, CDS RIC nomenclature, `TR.PARMIDSPREAD`/`MID_SPREAD`:
  LSEG Developer Community (CDS spreads / historical CDS prices) and library Build-Formula guides.
- CDX/iTraxx families, **March/September roll**, IG/HY, Main/Crossover/Senior-Sub Financials, tenors:
  Markit/IHS *CDS Indices Primer*; S&P DJI iTraxx/CDX methodology & roll announcements; ICE Markit iTraxx.
- SRT investor "writes a CDS on the obligor basket"; SRTx new-issue spread benchmark: Credit Benchmark
  SRT guide; Structured Credit Investor *SRTx*; BIS *Quarterly Review* on SRTs. DM/floater behaviour:
  `spreads-dm-calibration.md`, `credit-risk-parameter-theory.md`.
- FRN **quoted vs required (discount) margin** → price (par/premium/discount), DM definition: CFA Institute
  / AnalystPrep & IFT *Yield and Yield-Spread Measures for Floating-Rate Instruments*; BloombergPrep FRN DM;
  MathWorks `floatdiscmargin`. **Mark-to-market / calibrate-to-trade** fair value (observable trade →
  model recalibration; illiquid → model/broker inputs): Corporate Finance Institute & Wikipedia
  *Mark-to-market*; Structured Credit Investor FAQ.
