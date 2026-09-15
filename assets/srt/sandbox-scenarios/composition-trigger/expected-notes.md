# Expected handling — composition-based legal trigger

A correct run should:

1. **Treat the trigger as a legal term, not a model setting.** The CCC-concentration cap (7.5%) and the
   single-industry cap (20%) come from the indenture / CDS confirmation and must be *extracted*
   (`legal-inputs.md`), not assumed. State the source.
2. **Compute each metric from the *current* reference registry**, not from a prior period or a memory of
   the deal. CCC-or-below = 9.1% of current reference notional; largest industry = 17%.
3. **Conclude: CCC test BREACHED (9.1% > 7.5%); industry test NOT breached (17% < 20%).**
4. Because a test is breached, **do not silently continue pro-rata.** Route the pro-rata -> sequential
   switch as a **STOP + human approval** (model-update rule #8 / `srt-waterfall-and-triggers.md`); update
   `D25 ProRata_Amort` only once approved.
5. **Precondition check:** if the registry does not carry a **rating** column (for CCC) or an **industry**
   column (for concentration), the metric **cannot be derived** -> that is a **STOP for a missing required
   input**, never a "test passed." (Links to the granularity scenario.)
6. The mark must carry a **trigger attribution** ("vs. prior, because the CCC test breached and the
   waterfall switched to sequential"). Confirm the exact test definition (rating scale, numerator/
   denominator, cure provisions) **with your reviewer** before applying to a live mark.

This is **guidance**; thresholds here are synthetic sandbox values.
