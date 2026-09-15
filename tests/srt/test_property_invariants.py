"""Property-based & metamorphic invariants for the SRT deterministic core.

These complement the example-based suite. The pipeline (registry -> distributions ->
CDR/Severity, and RONA-weighted PD/LGD) is DETERMINISTIC, so the right rigor is not a
statistical test but (1) properties that must hold for ALL inputs and (2) metamorphic
relations (how outputs must move when inputs are transformed). Both directly target the
bug class that has actually bitten this project -- wrong-shaped / mis-weighted inputs.

Uses stdlib `random` with a fixed seed (no Hypothesis dependency, so it runs in every
env the rest of the suite does). Raise ITERS, or swap in Hypothesis, for a heavier sweep.
"""
import random
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
# registry scripts live under scripts/srt-registry-inputs/ in the plugin.
for _cand in (PLUGIN_ROOT / "scripts" / "srt-registry-inputs", PLUGIN_ROOT / "scripts"):
    if (_cand / "aggregate_to_cln.py").exists():
        sys.path.insert(0, str(_cand))
        break
import aggregate_to_cln as agg          # noqa: E402
import pd_lgd_weighted_average as pld    # noqa: E402

ITERS = 250
SEED = 20260608


def _rng():
    return random.Random(SEED)


class WeightedDistributionProperties(unittest.TestCase):
    """agg.weighted_distribution: a RONA-weighted proportion vector."""

    def _rows(self, rnd, buckets, key, n):
        return [{"rona": rnd.choice([1, 10, 250.5, 1e6]) * (rnd.random() + 1e-6),
                 key: rnd.choice(buckets + ["", None, "junk"])} for _ in range(n)]

    def test_proportions_sum_to_one_and_are_in_unit_interval(self):
        rnd = _rng()
        for _ in range(ITERS):
            rows = self._rows(rnd, list(agg.REGIONS), "region", rnd.randint(1, 12))
            dist, unb, tot = agg.weighted_distribution(
                rows, "rona", agg.bucket_region, agg.REGIONS, "region")
            for v in dist.values():
                self.assertGreaterEqual(v, -1e-12)
                self.assertLessEqual(v, 1 + 1e-9)
            if tot > 0:
                self.assertAlmostEqual(sum(dist.values()) + unb, 1.0, places=9)

    def test_scale_invariance(self):
        """Multiplying every weight by k>0 leaves the distribution unchanged."""
        rnd = _rng()
        for _ in range(ITERS):
            rows = self._rows(rnd, list(agg.LOAN_TYPES), "loan", rnd.randint(1, 10))
            k = rnd.choice([0.001, 3.5, 1000.0])
            base, _, _ = agg.weighted_distribution(
                rows, "rona", agg.bucket_loan_type, agg.LOAN_TYPES, "loan")
            scaled = [{**r, "rona": (agg.to_float(r["rona"]) or 0) * k} for r in rows]
            got, _, _ = agg.weighted_distribution(
                scaled, "rona", agg.bucket_loan_type, agg.LOAN_TYPES, "loan")
            for b in agg.LOAN_TYPES:
                self.assertAlmostEqual(base[b], got[b], places=9, msg=b)

    def test_permutation_invariance_and_zero_weight_noop(self):
        rnd = _rng()
        for _ in range(ITERS):
            rows = self._rows(rnd, list(agg.REGIONS), "region", rnd.randint(1, 10))
            base, _, _ = agg.weighted_distribution(
                rows, "rona", agg.bucket_region, agg.REGIONS, "region")
            shuffled = rows[:]
            rnd.shuffle(shuffled)
            shuffled += [{"rona": 0, "region": "US"}, {"rona": None, "region": "Eur"}]
            got, _, _ = agg.weighted_distribution(
                shuffled, "rona", agg.bucket_region, agg.REGIONS, "region")
            for b in agg.REGIONS:
                self.assertAlmostEqual(base[b], got[b], places=9, msg=b)


class SeverityCdrProperties(unittest.TestCase):
    def _rand_dist(self, rnd, keys):
        w = [rnd.random() for _ in keys]
        s = sum(w) or 1.0
        return {k: wi / s for k, wi in zip(keys, w)}

    def test_severity_in_unit_interval(self):
        rnd = _rng()
        for _ in range(ITERS):
            ld = self._rand_dist(rnd, agg.LOAN_TYPES)
            sev = agg.severity_from_loan_dist(ld, "Loan")
            self.assertIsNotNone(sev)
            self.assertGreaterEqual(sev, -1e-9)
            self.assertLessEqual(sev, 1 + 1e-9)

    def test_severity_increases_when_recovery_falls(self):
        """Metamorphic: shifting weight to the lowest-recovery loan type (Sn Unsecured,
        46.9) cannot DECREASE severity. Every other Loan bucket recovers more."""
        rnd = _rng()
        low = "Sn Unsecured"
        for _ in range(ITERS):
            ld = self._rand_dist(rnd, agg.LOAN_TYPES)
            sev0 = agg.severity_from_loan_dist(ld, "Loan")
            donor = rnd.choice([b for b in agg.LOAN_TYPES if b != low and ld[b] > 0] or [low])
            delta = ld[donor] * rnd.random()
            ld2 = dict(ld)
            ld2[donor] -= delta
            ld2[low] += delta
            sev1 = agg.severity_from_loan_dist(ld2, "Loan")
            self.assertGreaterEqual(sev1, sev0 - 1e-9)

    def test_cdr_at_least_floor(self):
        rnd = _rng()
        for _ in range(ITERS):
            rd = self._rand_dist(rnd, agg.RATING_BUCKETS)
            gd = self._rand_dist(rnd, agg.REGIONS)
            cdr = agg.cdr_from_dists(rd, gd, "Loan")
            self.assertGreaterEqual(cdr, agg.MIN_CDR - 1e-12)

    def test_cdr_nondecreasing_toward_ccc(self):
        """Metamorphic: moving rating weight to CCC (highest avg CDR) cannot DECREASE CDR."""
        rnd = _rng()
        for _ in range(ITERS):
            rd = self._rand_dist(rnd, agg.RATING_BUCKETS)
            gd = {r: (1.0 if r == "US" else 0.0) for r in agg.REGIONS}  # geo_leg = 1
            cdr0 = agg.cdr_from_dists(rd, gd, "Loan")
            donor = rnd.choice([b for b in agg.RATING_BUCKETS if b != "CCC" and rd[b] > 0] or ["CCC"])
            delta = rd[donor] * rnd.random()
            rd2 = dict(rd)
            rd2[donor] -= delta
            rd2["CCC"] += delta
            cdr1 = agg.cdr_from_dists(rd2, gd, "Loan")
            self.assertGreaterEqual(cdr1, cdr0 - 1e-12)


class PdLgdWeightingProperties(unittest.TestCase):
    """pld.weighted_average: RONA-weighted recovery; severity = 1 - it."""

    def _incl(self, rnd, n):
        out = []
        for i in range(n):
            rec = rnd.random()  # in [0, 1)
            w = rnd.choice([1, 5, 100.0, 2500.0]) * (rnd.random() + 1e-6)
            out.append(({"recovery": f"{rec}"}, w, f"ob{i}"))
        return out

    def test_weighted_recovery_and_severity_in_unit_interval(self):
        rnd = _rng()
        for _ in range(ITERS):
            incl = self._incl(rnd, rnd.randint(1, 12))
            tot = sum(w for _, w, _ in incl)
            wa, missing = pld.weighted_average(incl, tot, "recovery")
            self.assertEqual(missing, [])
            self.assertGreaterEqual(wa, -1e-12)
            self.assertLessEqual(wa, 1 + 1e-9)
            self.assertGreaterEqual(1 - wa, -1e-9)  # severity in [0,1] too

    def test_scale_invariance(self):
        rnd = _rng()
        for _ in range(ITERS):
            incl = self._incl(rnd, rnd.randint(1, 10))
            tot = sum(w for _, w, _ in incl)
            k = rnd.choice([0.01, 7.0, 1000.0])
            scaled = [(r, w * k, l) for r, w, l in incl]
            wa0, _ = pld.weighted_average(incl, tot, "recovery")
            wa1, _ = pld.weighted_average(scaled, tot * k, "recovery")
            self.assertAlmostEqual(wa0, wa1, places=9)

    def test_permutation_invariance(self):
        rnd = _rng()
        for _ in range(ITERS):
            incl = self._incl(rnd, rnd.randint(2, 10))
            tot = sum(w for _, w, _ in incl)
            shuffled = incl[:]
            rnd.shuffle(shuffled)
            wa0, _ = pld.weighted_average(incl, tot, "recovery")
            wa1, _ = pld.weighted_average(shuffled, tot, "recovery")
            self.assertAlmostEqual(wa0, wa1, places=9)

    def test_missing_value_blocks_not_fabricates(self):
        """A blank on any included row -> (None, [labels]); never a silent number."""
        incl = [({"recovery": "0.4"}, 60.0, "A"), ({"recovery": ""}, 40.0, "B")]
        wa, missing = pld.weighted_average(incl, 100.0, "recovery")
        self.assertIsNone(wa)
        self.assertEqual(missing, ["B"])

    def test_percent_or_fraction_are_equivalent(self):
        """'40%' and '0.40' must weight identically (the to_float convention)."""
        a, _ = pld.weighted_average([({"recovery": "40%"}, 10.0, "A")], 10.0, "recovery")
        b, _ = pld.weighted_average([({"recovery": "0.40"}, 10.0, "A")], 10.0, "recovery")
        self.assertAlmostEqual(a, b, places=12)


class AggregateEndToEndMetamorphic(unittest.TestCase):
    CFG = {"rona_col": "rona", "loan_type_col": "loan", "region_col": "region",
           "external_rating_cols": ["rating"], "bond_loan_flag": "Loan", "deal": "T"}

    def _rows(self, rnd, n):
        ratings = ["AAA", "BBB", "BB+", "B2", "Caa1", "", None]
        loans = ["Leveraged Loan", "Term Loan B", "Revolver", "Senior Secured", "Senior Unsecured"]
        regions = ["USA", "Germany", "India", "UAE", "China"]
        return [{"rona": rnd.choice([1, 10, 500.0]) * (rnd.random() + 1e-6),
                 "rating": rnd.choice(ratings),
                 "loan": rnd.choice(loans),
                 "region": rnd.choice(regions)} for _ in range(n)]

    def _assert_inputs_equal(self, a, b):
        for col in a:
            if isinstance(a[col], float):
                self.assertAlmostEqual(a[col], b[col], places=9, msg=col)
            else:
                self.assertEqual(a[col], b[col], col)

    def test_rona_scale_invariance_of_row_inputs(self):
        rnd = _rng()
        for _ in range(60):
            rows = self._rows(rnd, rnd.randint(2, 15))
            k = rnd.choice([0.01, 4.0, 1000.0])
            r0 = agg.cln_row_inputs(agg.aggregate(rows, self.CFG))
            scaled = [{**r, "rona": r["rona"] * k} for r in rows]
            r1 = agg.cln_row_inputs(agg.aggregate(scaled, self.CFG))
            self._assert_inputs_equal(r0, r1)

    def test_permutation_invariance_of_row_inputs(self):
        rnd = _rng()
        for _ in range(60):
            rows = self._rows(rnd, rnd.randint(2, 15))
            r0 = agg.cln_row_inputs(agg.aggregate(rows, self.CFG))
            shuffled = rows[:]
            rnd.shuffle(shuffled)
            r1 = agg.cln_row_inputs(agg.aggregate(shuffled, self.CFG))
            self._assert_inputs_equal(r0, r1)


class TotalFunctionProperties(unittest.TestCase):
    def test_bucket_rating_is_total_and_closed(self):
        rnd = _rng()
        alphabet = "ABCDEFG0123456789+-/ abcQRST"
        valid = set(agg.RATING_BUCKETS)
        for _ in range(ITERS):
            s = "".join(rnd.choice(alphabet) for _ in range(rnd.randint(0, 6)))
            self.assertIn(agg.bucket_rating(s), valid)
        self.assertEqual(agg.bucket_rating(None), "NA")
        self.assertEqual(agg.bucket_rating(""), "NA")

    def test_to_float_percent_is_value_over_100(self):
        rnd = _rng()
        for _ in range(ITERS):
            x = rnd.uniform(-5, 150)
            self.assertAlmostEqual(agg.to_float(f"{x}%"), x / 100.0, places=9)
            self.assertAlmostEqual(agg.to_float(f"{x}"), x, places=9)
        self.assertIsNone(agg.to_float(""))
        self.assertIsNone(agg.to_float("n/a"))


if __name__ == "__main__":
    unittest.main()
