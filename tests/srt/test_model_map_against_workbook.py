"""Independent workbook-contract check for the SRT model-mapping references.

Opens the REAL `Srt dcf.xlsm` with openpyxl ONLY (no in-house model / structured-products
skills) and verifies that the cell + named-range citations in the model-mapping
references match the live workbook:
  references/model-cell-map.md, dates-rates-daycount.md, pd-lgd-severity.md,
  spreads-dm-calibration.md.

The workbook lives in the configured analyst corpus, NOT in the package, so this
test SKIPS cleanly when openpyxl or the workbook is unavailable (CI, Plugin Eval, a
teammate without the corpus). On a machine that has the model, it is a real contract
test: it catches the doc drifting from the model (or the model being restructured).

Run directly:  python tests/srt/test_model_map_against_workbook.py
Locate-by-config: the workbook path is read from assets/srt/corpus.map.json
(corpus_root + model_skeleton.srt_dcf_model)."""
import importlib.util
import json
import re
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
ASSETS = PLUGIN_ROOT / "assets" / "srt"
REFS = ASSETS / "references"


def _workbook_path():
    try:
        cm = json.loads((ASSETS / "corpus.map.json").read_text(encoding="utf-8"))
        return Path(cm["corpus_root"]) / cm["model_skeleton"]["srt_dcf_model"]
    except Exception:
        return None

WB_PATH = _workbook_path()
HAVE = (
    importlib.util.find_spec("openpyxl") is not None
    and WB_PATH is not None
    and WB_PATH.exists()
)
WHY = "Srt dcf.xlsm or openpyxl not available (the model lives on the analyst's corpus, not in the package)"

# --- VERIFIED contract (checked against the live workbook 2026-06-08) ---
# named range -> a substring its refersTo must contain (the cell/range it points at)
NAMED_RANGES = {
    "ManualMode": "D6", "ScenNum": "D7", "Payment_Lag": "H4", "Val_Date": "D10",
    "Last_Portfolio_Update": "D11", "Issue_Date": "D14", "Adjusted_Issue_Date": "D15",
    "Issue_Price": "D16", "Replenishment_End_Date": "D17", "CF_Start": "D18", "Tenor": "D19",
    "Pay_EOM": "D20", "Libor_Fix": "D21", "Daycount_Basis": "D22", "Maturities_Are_Strats": "D23",
    "Prepay_In_Amort": "D24", "ProRata_Amort": "D25", "CDS_Maturity_Period": "D26",
    "CDR_RampName": "I6", "CDRScale": "I7", "CPR_RampName": "I8", "CPRScale": "I9",
    "Severity": "I10", "Severity_Liquidations": "H11", "Tranche_Names": "G16",
    "Is_Floating_Note": "H16", "Tranche_Rates": "I16", "Tranche_OrigBalances": "J16",
    "Discount_At_Float": "K16", "Discount_Margin": "P16", "Tranche_CurrLosses": "N16",
    "Tranche_Balances": "O16", "Current_Repaid": "L9", "Current_Loss": "L8", "Balance": "L10",
    "Writedown": "H34", "CleanPX": "H35",
    # OFFSET ranges — existence only
    "DF_Dates": None, "DF_DFs": None, "Scen_CDR": None, "Scen_Sev": None,
}

# (sheet, addr, kind, formula-substring-or-None)
CELLS = [
    ("Inputs", "D3", "FORMULA", None), ("Inputs", "D4", "FORMULA", None),
    ("Inputs", "D6", "CONST", None), ("Inputs", "D7", "CONST", None), ("Inputs", "D8", "CONST", None),
    ("Inputs", "D10", "CONST", None), ("Inputs", "D13", "FORMULA", "D12"),
    ("Inputs", "D14", "CONST", None), ("Inputs", "D15", "FORMULA", "Issue_Date"),
    ("Inputs", "D16", "CONST", None), ("Inputs", "D17", "CONST", None), ("Inputs", "D18", "CONST", None),
    ("Inputs", "D19", "CONST", None), ("Inputs", "D20", "CONST", None), ("Inputs", "D21", "CONST", None),
    ("Inputs", "D22", "CONST", None), ("Inputs", "D26", "FORMULA", None),
    ("Inputs", "H4", "CONST", None), ("Inputs", "H7", "CONST", None), ("Inputs", "H10", "CONST", None),
    ("Inputs", "H11", "CONST", None), ("Inputs", "H12", "CONST", None),
    ("Inputs", "I7", "FORMULA", "ManualMode"), ("Inputs", "I10", "FORMULA", "ManualMode"),
    ("Inputs", "L8", "FORMULA", "L4"), ("Inputs", "L10", "FORMULA", "Current_Loss"),
    ("Inputs", "L20", "FORMULA", "M34"), ("Inputs", "L30", "CONST", None),
    ("Inputs", "L32", "FORMULA", "96.1975"), ("Inputs", "L34", "FORMULA", "L30"),
    ("Inputs", "M34", "FORMULA", "L34"), ("Inputs", "H31", "FORMULA", "MATCH"),
    ("Inputs", "H34", "FORMULA", None), ("Inputs", "H35", "FORMULA", "INDEX"),
    ("Inputs", "H36", "FORMULA", "CleanPX"), ("Inputs", "M39", "FORMULA", "XIRR"),
    ("Inputs", "C30", "FORMULA", "Val_Date"), ("Inputs", "D30", "CONST", None),
    ("Spread Analysis", "D7", "FORMULA", None), ("Spread Analysis", "D8", "FORMULA", "D7"),
]

# the four references that make workbook-cell/named-range claims
MODEL_REFS = ["model-cell-map.md", "dates-rates-daycount.md",
              "pd-lgd-severity.md", "spreads-dm-calibration.md"]


def _kind(v):
    if v is None:
        return "EMPTY"
    return "FORMULA" if isinstance(v, str) and v.startswith("=") else "CONST"


def _norm(s):
    return re.sub(r"\s+", "", str(s)).upper()


@unittest.skipUnless(HAVE, WHY)
class ModelMapAgainstWorkbookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import openpyxl
        cls.wb = openpyxl.load_workbook(WB_PATH, data_only=False, keep_vba=True)
        cls.names = {}
        for name, obj in cls.wb.defined_names.items():
            cls.names[name] = getattr(obj, "value", None) or getattr(obj, "attr_text", None)

    def test_documented_named_ranges_resolve_to_expected_cells(self):
        bad = []
        for nm, exp in NAMED_RANGES.items():
            ref = self.names.get(nm)
            if ref is None:
                bad.append(f"{nm}: named range MISSING from workbook")
            elif exp is not None and exp not in str(ref).replace("$", ""):
                bad.append(f"{nm}: expected ~{exp}, workbook refersTo {ref}")
        self.assertEqual(bad, [], "named-range mismatches:\n  " + "\n  ".join(bad))

    def test_documented_cells_match_type_and_formula(self):
        bad = []
        for sheet, addr, exp_kind, substr in CELLS:
            if sheet not in self.wb.sheetnames:
                bad.append(f"{sheet}!{addr}: sheet missing"); continue
            v = self.wb[sheet][addr].value
            k = _kind(v)
            if k != exp_kind:
                bad.append(f"{sheet}!{addr}: got {k}, expected {exp_kind}")
            elif substr and _norm(substr) not in _norm(v):
                bad.append(f"{sheet}!{addr}: formula missing '{substr}' (got {str(v)[:60]})")
        self.assertEqual(bad, [], "cell type/formula mismatches:\n  " + "\n  ".join(bad))

    def test_named_ranges_cited_in_references_all_exist(self):
        """Every underscore-style named range cited in the four model refs must be a real defined name."""
        tok = re.compile(r"`([A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+)`")
        missing = []
        for fname in MODEL_REFS:
            text = (REFS / fname).read_text(encoding="utf-8")
            for name in set(tok.findall(text)):
                if name not in self.names:
                    missing.append(f"{fname} cites `{name}` which is not a workbook named range")
        self.assertEqual(missing, [], "referenced-but-undefined named ranges:\n  " + "\n  ".join(missing))


if __name__ == "__main__":
    unittest.main(verbosity=2)
