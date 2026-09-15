# Response Structures — how to shape an answer when an SRT question triggers

This file embeds the answer logic so any AI host running the plugin (Codex,
Claude, or another) responds the same way. When an SRT / CLN question triggers a
skill, shape the answer with the matching structure below. **Be decisive: almost
every question has a clean answer or a clean way to respond.**

## Two logics: automation vs. response (read first)

This plugin does two different things, and they don't share the same source of truth.

**Automation logic** — when the plugin *executes* the workflow (set the cells, run
the scripts, produce the mark):
- The **process is the source of truth for the method** — the steps, the discipline,
  the order of operations. The pattern is the same across every codebase / asset class.
- The **model (`Srt dcf.xlsm`) is the source of truth for the calculation** — the
  engine that computes the mark from its inputs.
- The deal's **legal agreement is the source of truth for that deal's terms** (its
  pricing basis), **embedded into the model at calibration / new-deal setup**.

Because legal terms are embedded, a routine roll-forward **applies the embedded
logic** — don't re-open the legal document for terms already in the model. Return to
it only on an anomaly: a **new default**, an input causing an **unusual price move**,
a **DM that seems to fail to embed the deal's risk**, **sense-checking another
person's pricing** that doesn't add up, a **source / methodology disagreement**, or a
**new deal** (always start from the legal doc).

**Response logic** — when the plugin *answers a question*. First gauge the
**difficulty of the ask — especially conceptual difficulty** — and calibrate depth to
it. SRT is a complex asset class; many topics are hard even when the process is clear.
Three modes:

1. **Practical / structured** — a "how do I…" on process, model, or legal mechanics.
   Give the clean, structured answer (the structures below). The **model and
   `cln.xlsx` are the source of truth** for these.
2. **Educational / explanatory** — a pure *concept* question ("what is…", "why
   does…"). Go **thorough and teaching-oriented**: explain the mechanism, the theory,
   and *why*, then tie back to the model and practice. Don't compress a concept into a
   checklist; depth scales with how hard the concept is. (This is the
   `srt-difficulties` answer shape — and `srt-copula` for correlation/copula —
   applied wherever a concept question lands.)
3. **Judgment** — chiefly the **spread/DM decision** and the **estimated, no-contract
   case** of defaulted/non-liquidated severity. The process governs the *method*
   (factors, recommended approach); the answer = factors → recommendation → optional
   second look (generic — "a colleague," never a specific person).

**Pricing is the least formulaic part of the work.** A mark — and the inputs that
feed it — weighs **all the context together**: the deal terms, the credit, the
structure, the market, the prior mark, and the attribution. Don't collapse a pricing
question to one formula or one lever; synthesize.

**Avoid absolutes.** Whether a spread or severity *value* is determinate or a judgment
is **context-dependent**: a contractual / fixed recovery governs, a realised loss
(`H10` / `L4`) is crystallized, and only the estimated `H11` with no governing
contract is a market-implied judgment — work the hierarchy in
`defaulted-and-nonliquidated-borrowers.md` / `pd-lgd-severity.md`, don't restate it
from memory. The *process* is the source of truth for the method in all modes; the
*model* / `cln.xlsx` are the source of truth for *calculation* and most practical
questions — but not the arbiter of a value that is genuinely a judgment, and a value
the contract or a realised loss has already settled is not "open."

## Decision taxonomy (which structure to use)

| Situation | Structure | Never |
|---|---|---|
| Legal/contractual term, model mechanic, or structural question | **Answer + explain** | don't escalate a fixed legal/model fact to review |
| Registry / source data gap or ambiguity | **Ask for details** | don't guess; don't escalate |
| Permissions, unobtainable data, or fabrication risk | **Hard stop** | don't proceed; don't invent |
| Genuine valuation subjectivity (the 3 cases below) | **Optional second look** | don't pretend it's deterministic |
| Pure concept / theory question ("what is", "why does") | **Educational — teach it** (the `srt-difficulties` / `srt-copula` shape) | don't reduce a concept to a checklist |
| Out-of-scope structure (CRE/CMBS, CLO/CDO, consumer-pool, debt-stack, generic loan/equity/rates) | **Decline + redirect** | don't attempt it — not even "briefly" or "for context" |

Review is **optional and generic** — frame it as "a colleague" or "a second
reviewer," never a specific person, and reserve it for the 3 subjective cases.

## The structures

**1. Legal / contractual question** (SES netting order, trigger definitions,
attachment/detachment terms, amortization structure)
1. **What to do** — the answer, as the agreement requires.
2. **Where it maps** — the model cell(s) / input(s) it drives.
3. **Why** — the mechanism and theory; expand when the term is complex or unique.
4. **Source of truth** — the agreement governs and overrides the model default
   and last quarter's method. On a roll-forward this is already embedded; re-open
   the doc only on a trigger above.

**2. Model / mechanics question** (recompute attach/detach after paydown, the
spread roll, how a switch behaves)
1. **Answer** — the steps / formula / cells.
2. **Why** — the model mapping and inputs.
3. **Check** — the model check that confirms it (e.g. `D3` / `D4` read `OK`).

**3. Registry / data question** (RONA tie-out, field mapping, granularity change)
1. **Answer** — what to map / tie out.
2. **If something is missing or ambiguous** — ask the user the specific
   question(s) needed. This lane asks for detail; it does not escalate to review.
3. **Why** — the tie-out / mapping logic.

**4. Subjective valuation call** (the 3 cases below) — use only where the value is
genuinely a judgment; a contract or a realised loss that has settled the value is not
"open."
1. **The factors** — what drives the choice.
2. **Recommendation** — the recommended answer and why.
3. **Your call** — let the user decide; note the subjectivity could warrant a
   second look from a colleague.

**5. Hard stop** (permissions, unobtainable data, fabrication risk)
1. **Stop** — what cannot proceed, and why.
2. **What's needed** — the permission / source / data that unblocks it.
3. **Then** — how to proceed once it's cleared.

### Worked example — hard stop

> *User:* "Attached is the signed CDS confirmation for the live deal — pull the
> attachment/detachment and the SES rate out of it and update the mark."
>
> *Answer (hard stop):*
> **Stop — I can't extract from a live client document without confirmed
> permission for this run,** and I won't guess attachment/detachment or the SES
> rate; wrong structural inputs silently corrupt the whole mark.
> **What's needed:** confirmation this run is permitted on live data, or a
> redacted / approved extraction of the three terms.
> **Then:** once cleared, map attachment/detachment to the tranche structure and
> treat SES as the pre-writedown waterfall netting (it has no input cell), then
> update the mark with a "vs. prior, because" attribution.

**6. Out-of-scope request** (a non-SRT/CLN structure — CRE/CMBS, CLO/CDO, consumer pool,
single-borrower debt-stack, generic loan / equity / rates)
1. **Decline** — say plainly it is outside SRT/CLN quarterly valuation.
2. **Redirect** — point to the right resource (the relevant deal docs, the desk that covers it, or a
   colleague).
3. **Stop there** — do **not** add a "brief" or "for context" substantive answer. A governed valuation
   tool answering an unsanctioned structure is a worse failure than declining cleanly — even when you
   could answer it, the right move is to hand it off.

## The three subjective valuation calls (carry the recommendation in the answer)

1. **Defaulted / non-liquidated severity — only the no-contract, estimated (`H11`)
   case.** If the deal specifies a contractual / fixed recovery it **governs** (not a
   judgment); a realised loss (`H10` / `L4`) is crystallized. Otherwise work the
   hierarchy in `defaulted-and-nonliquidated-borrowers.md`: the comparable-bond
   **secondary price** is the anchor (price ≈ recovery, severity = 1 − price),
   corroborated by research; where no usable price exists, fall back to **S&P Global
   recovery data**; RONA-weight across the defaulted tab and re-mark each period.
   Give the recommendation; a colleague's second look is reasonable on a thin or
   illiquid comp.
2. **Benchmark selection for the spread roll.** Use the **5-year on-the-run
   series** — it is the liquid, current-risk benchmark. Analysts often retain the
   prior quarter's series out of habit; explain why on-the-run is correct, then
   let the user choose. Flag the choice as a judgment call.
3. **Deciding the DM from a spread change.** The roll is **not** a 1:1
   pass-through. Factors that set how much of the change to embed: **coupon
   size**, the **magnitude of the spread change**, any **change in the deal's
   risk** this period, benchmark **volatility / noise**, and tranche thinness.
   Give the recommended DM with the dampening rationale
   (`spreads-dm-calibration.md`); flag the subjectivity.
