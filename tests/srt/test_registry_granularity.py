"""Registry -> CLN aggregation contract (the redefined granularity test).

Registries vary in columns, in which agency rates which name, and in granularity
(obligor-level one quarter, pre-bucketed the next). The contract is that the
aggregation ALWAYS lands in one of two methodologically-consistent paths and ALWAYS
maps to the fixed CLN buckets, regardless of that variation:

  ratings   -> IG / BB / B / CCC / NA   (internal ratings mapped to external first)
  loan type -> Leverage Loan / Sn Unsecured / Sn Secured / Term Loans / Revolver /
               Trade Finance / Property
  geography -> US / Eur / Middle East / India / EM/Asia

The CDR/Severity replicas are anchored to two live `cln.xlsx` rows (0.2527 and
0.5229) so a drift in the mirrored Parameters constants is caught here.

Pure-function tests over `aggregate_to_cln`; no workbook or network needed.
"""
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
# registry scripts live under scripts/srt-registry-inputs/ in the plugin.
for _cand in (PLUGIN_ROOT / "scripts" / "srt-registry-inputs", PLUGIN_ROOT / "scripts"):
    if (_cand / "aggregate_to_cln.py").exists():
        sys.path.insert(0, str(_cand))
        break
import aggregate_to_cln as agg  # noqa: E402

LOAN_CFG = {"rona_col": "rona", "loan_type_col": "loan", "region_col": "region",
            "external_rating_cols": [], "bond_loan_flag": "Loan", "deal": "T"}


class BucketingTests(unittest.TestCase):
    def test_rating_buckets_sp_and_moody_scales(self):
        for raw, exp in [("AAA", "IG"), ("BBB-", "IG"), ("Baa2", "IG"),
                         ("BB+", "BB"), ("Ba1", "BB"), ("B2", "B"), ("B-", "B"),
                         ("CCC+", "CCC"), ("Caa1", "CCC"), ("Ca", "CCC"), ("D", "CCC"),
                         ("", "NA"), (None, "NA")]:
            self.assertEqual(agg.bucket_rating(raw), exp, raw)

    def test_loan_type_buckets_from_varied_descriptors(self):
        for raw, exp in [("Leveraged Loan", "Leverage Loan"), ("Term Loan B", "Term Loans"),
                         ("RCF / Revolver", "Revolver"), ("Senior Secured Notes", "Sn Secured"),
                         ("Senior Unsecured", "Sn Unsecured"), ("Trade Finance facility", "Trade Finance"),
                         ("Commercial Real Estate", "Property"), ("CRE loan", "Property"),
                         # review 2026-09-11 (T6/C5): "cre" must not match the substring of "credit"
                         ("Revolving Credit Facility", "Revolver"),
                         ("Senior Secured Credit Facility", "Sn Secured"),
                         ("Senior Unsecured Credit Facility", "Sn Unsecured"),
                         ("Term Loan B (Credit Agreement)", "Term Loans")]:
            self.assertEqual(agg.bucket_loan_type(raw), exp, raw)

    def test_region_buckets_and_the_positional_finding(self):
        self.assertEqual(agg.bucket_region("United States"), "US")
        self.assertEqual(agg.bucket_region("Germany"), "Eur")
        self.assertEqual(agg.bucket_region("India"), "India")
        self.assertEqual(agg.bucket_region("UAE"), "Middle East")
        self.assertEqual(agg.bucket_region("China"), "EM/Asia")
        # the file multiplies India positionally by the EM&FM multiplier (0.5549)
        self.assertAlmostEqual(agg.GEO_MULT[agg.REGIONS.index("India")], 0.5548817465130383)


class ExternalRatingSelectionTests(unittest.TestCase):
    def test_most_populated_column_with_per_obligor_fallback(self):
        # Moody filled 3/4, S&P fills the one Moody misses -> full coverage, no NA.
        rows = [
            {"rona": "250", "Moody": "A2", "SP": ""},
            {"rona": "250", "Moody": "Ba1", "SP": ""},
            {"rona": "250", "Moody": "", "SP": "BB+"},   # falls back to S&P
            {"rona": "250", "Moody": "Caa1", "SP": "CCC"},
        ]
        cfg = dict(LOAN_CFG, external_rating_cols=["SP", "Moody"])
        res = agg.aggregate(rows, cfg)
        rd = res["rating_distribution"]
        self.assertAlmostEqual(rd["NA"], 0.0, places=9)  # everyone resolved
        self.assertAlmostEqual(rd["IG"], 0.25)
        self.assertAlmostEqual(rd["BB"], 0.50)
        self.assertAlmostEqual(rd["CCC"], 0.25)


class GranularityAgnosticTests(unittest.TestCase):
    def test_obligor_level_and_prebucketed_give_same_rating_distribution(self):
        cfg = dict(LOAN_CFG, external_rating_cols=["rating"])
        fine = [{"rona": "250", "rating": "BBB"}, {"rona": "250", "rating": "BBB"},
                {"rona": "300", "rating": "BB"}, {"rona": "200", "rating": "CCC"}]
        coarse = [{"rona": "500", "rating": "BBB"}, {"rona": "300", "rating": "BB"},
                  {"rona": "200", "rating": "CCC"}]
        a = agg.aggregate(fine, cfg)["rating_distribution"]
        b = agg.aggregate(coarse, cfg)["rating_distribution"]
        for k in agg.RATING_BUCKETS:
            self.assertAlmostEqual(a[k], b[k], places=9, msg=k)
        self.assertAlmostEqual(sum(a.values()), 1.0, places=9)


class GoldenCdrSeverityTests(unittest.TestCase):
    def test_severity_matches_live_row_a(self):  # 20.58% Term + 79.42% Revolver -> 0.2527
        rows = [{"rona": "205.81", "loan": "Term Loan"}, {"rona": "794.19", "loan": "Revolver"}]
        res = agg.aggregate(rows, LOAN_CFG)
        self.assertAlmostEqual(res["self_check_severity"], 0.2527, places=3)

    def test_severity_matches_live_row_b(self):  # 94.33% Sn Unsec + 5.67% Sn Sec -> 0.5229
        rows = [{"rona": "943.3", "loan": "Senior Unsecured"}, {"rona": "56.7", "loan": "Senior Secured"}]
        res = agg.aggregate(rows, LOAN_CFG)
        self.assertAlmostEqual(res["self_check_severity"], 0.5229, places=3)

    def test_cdr_uses_ccc_rate_geo_multiplier_and_floor(self):
        # 100% CCC, 100% US (mult 1.0), Loan -> 7.89796 * 1.0 / 100
        us = agg.aggregate([{"rona": "100", "rating": "CCC", "region": "United States"}],
                           dict(LOAN_CFG, external_rating_cols=["rating"]))
        self.assertAlmostEqual(us["self_check_cdr"], 0.0789796, places=5)
        # 100% CCC, 100% India -> positionally multiplied by 0.5549
        ind = agg.aggregate([{"rona": "100", "rating": "CCC", "region": "India"}],
                            dict(LOAN_CFG, external_rating_cols=["rating"]))
        self.assertAlmostEqual(ind["self_check_cdr"], 0.0789796 * 0.5548817465130383, places=5)
        # low-risk pool floors at minCDR
        ig = agg.aggregate([{"rona": "100", "rating": "AAA", "region": "United States"}],
                           dict(LOAN_CFG, external_rating_cols=["rating"]))
        self.assertAlmostEqual(ig["self_check_cdr"], agg.MIN_CDR, places=9)


class PathConsistencyTests(unittest.TestCase):
    def test_new_deal_without_pdlgd_aggregates(self):
        path, stop, _ = agg.choose_path(None, registry_has_obligor_pdlgd=False, new_deal=True)
        self.assertEqual(path, "aggregate"); self.assertFalse(stop)

    def test_new_deal_with_pdlgd_uses_obligor(self):
        path, stop, _ = agg.choose_path(None, True, True)
        self.assertEqual(path, "obligor"); self.assertFalse(stop)

    def test_obligor_calibrated_continues_when_tape_still_has_pdlgd(self):
        path, stop, _ = agg.choose_path("obligor", True, False)
        self.assertEqual(path, "obligor"); self.assertFalse(stop)

    def test_obligor_calibrated_stops_when_tape_loses_pdlgd(self):
        _, stop, msg = agg.choose_path("obligor", False, False)
        self.assertTrue(stop); self.assertIn("STOP", msg)

    def test_aggregate_calibrated_stops_when_tape_gains_pdlgd(self):
        _, stop, msg = agg.choose_path("aggregate", True, False)
        self.assertTrue(stop)
        self.assertIn("methodology-driven", msg)  # explains the variance, requires human review

    def test_aggregate_calibrated_continues_without_pdlgd(self):
        path, stop, _ = agg.choose_path("aggregate", False, False)
        self.assertEqual(path, "aggregate"); self.assertFalse(stop)


class InternalRatingTests(unittest.TestCase):
    def test_internal_only_without_mapping_flags_and_stops(self):
        rows = [{"rona": "100", "internal": "Grade 3", "loan": "Term Loan"}]
        cfg = dict(LOAN_CFG, external_rating_cols=[], internal_rating_cols=["internal"],
                   internal_to_external_map=None)
        res = agg.aggregate(rows, cfg)
        self.assertTrue(res["internal_rating_flag"])
        self.assertTrue(res["stops"])

    def test_internal_with_mapping_resolves(self):
        rows = [{"rona": "100", "internal": "Grade 3", "loan": "Term Loan"}]
        cfg = dict(LOAN_CFG, external_rating_cols=[], internal_rating_cols=["internal"],
                   internal_to_external_map={"Grade 3": "BB"})
        res = agg.aggregate(rows, cfg)
        self.assertFalse(res["internal_rating_flag"])
        self.assertAlmostEqual(res["rating_distribution"]["BB"], 1.0)


class ClnRowInputsTests(unittest.TestCase):
    def test_emits_input_columns_only_not_formula_columns(self):
        rows = [{"rona": "100", "rating": "BBB", "loan": "Term Loan", "region": "United States"}]
        res = agg.aggregate(rows, dict(LOAN_CFG, external_rating_cols=["rating"]))
        cols = agg.cln_row_inputs(res)
        # writes C,D:H,I,O:U,V:Z -- never J:N (renorm), AB (CDR) or AC (Severity)
        for forbidden in ("J", "K", "L", "M", "N", "AB", "AC"):
            self.assertNotIn(forbidden, cols)
        self.assertEqual(cols["I"], "Yes")           # Include NA = Yes per protocol
        self.assertAlmostEqual(cols["D"], 1.0)       # 100% IG
        self.assertAlmostEqual(cols["R"], 1.0)       # 100% Term Loans
        self.assertAlmostEqual(cols["V"], 1.0)       # 100% US


if __name__ == "__main__":
    unittest.main()
