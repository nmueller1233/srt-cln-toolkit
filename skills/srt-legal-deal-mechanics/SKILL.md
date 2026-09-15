---
name: srt-legal-deal-mechanics
description: Use when SRT/CLN work involves legal terms, CDS confirmations, indentures/offering memos, SES, triggers, amortization, funded/unfunded exposure, calls, reserves, step-ups, settlement, pricing drivers, or mapping terms to Srt dcf.xlsm.
---

# SRT Legal Deal Mechanics

Use this lane to explain what the contract says and how terms map before
calibration, update, or review. Deal documents and approved extractions control.

Load `../../assets/srt/references/core-contract.md`. Ask for the legal document
or approved extraction when mapping or a disputed mechanic depends on deal text.

Primary mapped cells: `D12`, `D14`, `D16:D22`, `D23:D25`, `D27`, `H3:H4`,
`H10:H12`, `G16:K20`, and `L3`. Also capture SES, replenishment, triggers,
split amortization, calls, step-ups, reserves, funded/unfunded treatment,
settlement timing, and credit-event terms.

Explain fixed legal mechanics directly. The agreement is the pricing basis and
outranks model defaults. Re-open it on a roll-forward only for anomalies: new
default, unusual price move, DM/risk mismatch, odd third-party mark, or
source/methodology dispute.

References: `legal-inputs.md`, `srt-waterfall-and-triggers.md`, `ses.md`,
`model-cell-map.md`, `response-structures.md`.

Use `srt-calibration` for the par solve and `srt-quarterly-model-update` for
current-period facts.
