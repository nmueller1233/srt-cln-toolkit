# Defaulted and Non-Liquidated Borrowers

> Guidance only. This file supports the `H11` treatment for names that have defaulted but whose final recovery/loss is not yet fixed. It does not override the legal documents, registry, `pd-lgd-severity.md`, `model-cell-map.md`, or reviewer approval.

## Two states

| State | Loss status | Severity | Treatment |
|---|---|---|---|
| Defaulted and liquidated | Final/realised | `H10` | Fixed loss; do not re-estimate |
| Defaulted, not yet liquidated | Estimated/workout | `H11` | Re-mark each period until final recovery is known |

A newly defaulted name usually starts in the second state: the credit event has occurred, but the final loss is not yet known.

## Core rules

- Remove the name from the forward-performing PD pool; it cannot default again.
- Keep its EAD/RONA in the registry tie-out until the deal/report/model removes or writes it down.
- Do not overwrite realised `L4`/`H10` treatment with a later market-implied estimate.
- Apply SES only if the deal legally provides it; `ses.md` controls that step.
- Carry recovery timing through `H12` when the expected workout date matters.

## H11 severity hierarchy

Work per obligor, then RONA-weight the result across the defaulted/non-liquidated bucket:

1. Contract first. If the deal, CDS terms, or client-provided instruction defines fixed recovery/loss treatment, use that and cite it.
2. If no contractual figure controls, use Debtwire/restructuring research to classify the event and recovery direction.
3. Anchor the estimate with the most comparable secondary bond/loan price where available. Match issuer, seniority, lien/security, sector, jurisdiction, and tenor as closely as possible.
4. Convert recovery to severity and RONA-weight:

```text
H11 severity = 1 - sum(recovery_i * RONA_i) / sum(RONA_i)
```

Stop on missing recovery, missing RONA, unclear seniority, or an unsupported comparable.

## Restructuring coverage

Restructuring can be a default or credit event, especially distressed exchanges, missed payments, bankruptcy filings, or coercive liability-management transactions. It should not automatically be marked as bankruptcy-level loss.

Use the legal definition first: some synthetic/CDS terms treat restructuring differently, and deliverable obligations or auction mechanics may change the recovery result. Then use the economics:

- A distressed exchange often implies higher recovery than bankruptcy.
- Exchange consideration, post-announcement prices, lien changes, uptiers/drop-downs, and sponsor support are recovery evidence.
- A market price is a current fair-value estimate, not final realised recovery.
- A restructuring can remain unresolved and later re-default; keep it in `H11` until final treatment is known.

## Evidence checklist

Record:

- Registry path and defaulted/non-liquidated tab total.
- Default date/event and whether it is new this period.
- Contract clause or client instruction if one governs.
- Debtwire/news citations used for restructuring or workout status.
- Comparable price source, date, instrument, seniority/lien rationale, and percent/decimal convention.
- Per-name recovery/severity, RONA, weighted `H11`, recovery lag `H12`, SES treatment, and reviewer.

## Common errors

- Double-counting the same name in forward PD and defaulted loss.
- Dropping the defaulted name from notional before the registry/model does.
- Treating estimated recovery as realised.
- Using a wrong-seniority comparable as the recovery anchor.
- Equal-weighting names instead of RONA-weighting.
- Applying SES without legal support.

## Further review

- Moody's `Annual Default Study` and Ultimate Recovery Database documentation.
- S&P materials on distressed exchanges, selective default, and recovery ratings.
- ISDA `Credit Event Process` and ICE credit event auction primers for CDS-style settlement.
- Current Debtwire or approved news/research for borrower-specific restructuring facts.

## Where this file stops

If the event classification, recovery basis, legal settlement, registry tie-out, or reviewer approval is unclear, stop and escalate rather than inventing a severity.
