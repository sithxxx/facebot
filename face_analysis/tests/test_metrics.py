import unittest
import numpy as np
from face_analysis.metrics import symmetry, eyes, nose, jaw_chin, lips, forehead
from face_analysis.detector import LANDMARK_INDICES

class TestMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a basic symmetric dummy face (478 points)
        cls.pts = np.zeros((478, 2))
        
        # Midline: x=50
        cls.pts[LANDMARK_INDICES["nose_bridge"]] = [50, 20]
        cls.pts[LANDMARK_INDICES["chin_bottom"]] = [50, 80]
        cls.pts[LANDMARK_INDICES["nose_tip"]] = [50, 50]
        
        # Cheeks: x=20, 80
        cls.pts[LANDMARK_INDICES["left_cheek"]] = [20, 45]
        cls.pts[LANDMARK_INDICES["right_cheek"]] = [80, 45]
        
        # Eyes
        cls.pts[LANDMARK_INDICES["left_eye_outer"]] = [30, 35]
        cls.pts[LANDMARK_INDICES["left_eye_inner"]] = [40, 35]
        cls.pts[LANDMARK_INDICES["right_eye_inner"]] = [60, 35]
        cls.pts[LANDMARK_INDICES["right_eye_outer"]] = [70, 35]
        cls.pts[LANDMARK_INDICES["left_eye_top"]] = [35, 33]
        cls.pts[LANDMARK_INDICES["left_eye_bottom"]] = [35, 37]
        cls.pts[LANDMARK_INDICES["right_eye_top"]] = [65, 33]
        cls.pts[LANDMARK_INDICES["right_eye_bottom"]] = [65, 37]
        
        # Nose
        cls.pts[LANDMARK_INDICES["left_nose_wing"]] = [45, 50]
        cls.pts[LANDMARK_INDICES["right_nose_wing"]] = [55, 50]
        
        # Jaw
        cls.pts[LANDMARK_INDICES["left_jaw"]] = [30, 70]
        cls.pts[LANDMARK_INDICES["right_jaw"]] = [70, 70]
        
        # Mouth
        cls.pts[LANDMARK_INDICES["mouth_left"]] = [40, 65]
        cls.pts[LANDMARK_INDICES["mouth_right"]] = [60, 65]
        cls.pts[LANDMARK_INDICES["upper_lip_top"]] = [50, 62]
        cls.pts[LANDMARK_INDICES["lower_lip_bottom"]] = [50, 68]
        cls.pts[LANDMARK_INDICES["upper_lip_bottom"]] = [50, 64]
        cls.pts[LANDMARK_INDICES["lower_lip_top"]] = [50, 66]
        
        # Brows
        cls.pts[LANDMARK_INDICES["left_brow_inner"]] = [35, 30]
        cls.pts[LANDMARK_INDICES["right_brow_inner"]] = [65, 30]
        cls.pts[LANDMARK_INDICES["left_brow_outer"]] = [25, 30]
        cls.pts[LANDMARK_INDICES["right_brow_outer"]] = [75, 30]

    def test_symmetry(self):
        val = symmetry.face_symmetry(self.pts)
        self.assertGreater(val, 0.9)

    def test_proportions(self):
        val = symmetry.face_proportions(self.pts)
        self.assertGreater(val, 0)

    def test_eye_metrics(self):
        self.assertGreater(eyes.eye_size(self.pts), 0)
        self.assertEqual(eyes.eye_tilt(self.pts), 0) # Symmetric eyes

    def test_nose_metrics(self):
        self.assertGreater(nose.nose_width(self.pts), 0)
        self.assertGreater(nose.nose_length(self.pts), 0)

    def test_lip_metrics(self):
        self.assertGreater(lips.lip_fullness(self.pts), 0)
        self.assertAlmostEqual(lips.lip_proportions(self.pts), 1.0)

if __name__ == "__main__":
    unittest.main()
