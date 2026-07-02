import unittest
from face_analysis.scorer import raw_to_score
from face_analysis.norms import NORMS


class TestScorer(unittest.TestCase):
    def test_raw_to_score_at_median(self):
        # A directional (+1) metric scores the midpoint (5.5) exactly at the median.
        med = NORMS["male"]["face_symmetry"]["median"]
        score, sigma = raw_to_score(med, "face_symmetry", "male")
        self.assertAlmostEqual(score, 5.5)
        self.assertAlmostEqual(sigma, 0.0)

    def test_raw_to_score_high_symmetry(self):
        # Higher than median (direction +1) should beat the at-median score.
        med = NORMS["male"]["face_symmetry"]["median"]
        std = NORMS["male"]["face_symmetry"]["std"]
        score, _ = raw_to_score(med + std, "face_symmetry", "male")
        self.assertGreater(score, 5.5)

    def test_raw_to_score_low_nose_width(self):
        # For nose_width, lower is better (direction -1).
        score_high, _ = raw_to_score(0.3, "nose_width", "male")
        score_low, _ = raw_to_score(0.2, "nose_width", "male")
        self.assertGreater(score_low, score_high)

    def test_proximity_metric_peaks_at_median(self):
        # A proximity (direction 0) metric peaks at 10 at the median and
        # decreases symmetrically — it must NOT be capped at 5.0 (the old bug).
        med = NORMS["male"]["face_proportions"]["median"]
        std = NORMS["male"]["face_proportions"]["std"]
        at_median, _ = raw_to_score(med, "face_proportions", "male")
        off_median, _ = raw_to_score(med + std, "face_proportions", "male")
        self.assertAlmostEqual(at_median, 10.0)
        self.assertLess(off_median, at_median)

    def test_raw_to_score_clamping(self):
        score, _ = raw_to_score(10.0, "face_symmetry", "male")
        self.assertEqual(score, 10.0)
        score, _ = raw_to_score(0.0, "face_symmetry", "male")
        self.assertEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
