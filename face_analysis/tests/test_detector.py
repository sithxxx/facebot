import unittest
import numpy as np
from face_analysis.detector import FaceDetector, detect_face

class TestDetector(unittest.TestCase):
    def test_detector_initialization(self):
        detector = FaceDetector()
        self.assertIsNotNone(detector.face_mesh)

    def test_detect_face_no_image(self):
        # Should return None if image path is invalid
        result = detect_face("non_existent_image.jpg")
        self.assertIsNone(result)

    def test_detect_face_dummy_array(self):
        # This might fail without a real face, but we check if it handles the input
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = detect_face(dummy_img)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
