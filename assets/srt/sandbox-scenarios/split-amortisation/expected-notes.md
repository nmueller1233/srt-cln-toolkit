# Expected handling — split / per-tranche amortisation

The deal amortises the **senior sequentially** but the **junior/mezz pro-rata**. The model controls
amortisation with a **single deal-level boolean, `D25 ProRata_Amort`** — there is no per-tranche control.

A correct run should:

1. **Recognise the mismatch:** one flag cannot represent two mechanisms at once. Setting `D25 = TRUE`
   mis-amortises the senior; `D25 = FALSE` mis-amortises the junior. Either choice is silently wrong.
2. **NOT pick a flag and proceed.** This is the failure mode the test guards against.
3. State that this needs your reviewer with the model-expressiveness gap stated plainly, and agree a
   representation before producing a mark: separate per-tranche runs with documented scope, an approved
   structural workaround, or a model change.
4. Keep the deliverable **not client-ready** until the representation is agreed and a human reviews it.

This connects to `model-cell-map.md` (`D25`) and `srt-waterfall-and-triggers.md`
("Split / per-tranche amortisation"). **Guidance** — confirm the actual amortisation terms from the
indenture with your reviewer.
