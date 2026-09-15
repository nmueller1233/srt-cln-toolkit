# Data redaction — deal references removed

The two workbooks the toolkit operates on (`Srt dcf.xlsm`, `cln.xlsx`) are **not included in this
repository**. When a copy is shared, **every deal / comparable reference is replaced by a generic
placeholder** (`Deal A`, `Deal B`, … and `Comparable 1`–`Comparable 5`) and the live-data ticker cache is
cleared; this file records how that is done.

## How redaction is done — and why by hand
Both workbooks are **S&P Capital IQ add-in, macro-enabled models** with live CDS/rate connections and
100+ named ranges. **Redact in Excel with Find & Replace ("Within: Workbook"), not with a script** — a
programmatic re-save silently drops the CapIQ connections and any charts. The exact cell-by-cell map for the
*original* files is held privately by the model owner (it necessarily lists the real names).

## Sample models
No sample workbooks are included in this repository.

## Redacting your own workbook
Open it in Excel → `Ctrl+H` → "Within: Workbook" → replace each deal / obligor / comparable name and any
vendor ticker with a generic placeholder → save. Then eyeball the deal-name columns and any single-name CDS
comparable cell to confirm nothing slipped through. Always keep an unredacted backup.
