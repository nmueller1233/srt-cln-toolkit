# Calculation assumptions

This reference is retained at the path cited by the Python helpers. For commands, inputs and outputs, see [the script guide](../docs/tools/scripts.md).

- The shadow calculation applies the benchmark change divided by the dampening divisor to the prior DM. The workbook calculates its valuation DM through its own multiplier formula. Confirm workbook units and compare the two outputs; take the mark from the workbook.
- The shadow estimate uses a linear loss-to-writedown adjustment and a zero rate contribution. Interpret it as a diagnostic comparison with the recorded mark.
- The CLN aggregator uses its documented rating, loan and region constants and positional mapping. It does not filter defaulted rows or renormalize unmapped exposure. Select the population and inspect the distribution sums before use.
- Direct PD and LGD averages use exposure weights. Their product reproduces an exposure-weighted expected loss only under the stated PD/LGD dependence assumption.
- The new-deal par solve uses the inputs present at that step. Record them and any reason for a subsequent re-solve; retain the prescribed sequence and the origination anchor on quarterly updates.
- The CLN writer saves to the path supplied. Select a workbook copy and follow the documented inputs-row and workbook-feature constraints.

Detailed procedures: [DM and calibration](../assets/srt/references/spreads-dm-calibration.md), [CLN aggregation](../assets/srt/references/cln-aggregation.md), [credit inputs](../assets/srt/references/pd-lgd-severity.md), and [the fifteen-step process](../assets/srt/references/process.md).
