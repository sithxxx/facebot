import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from bot.services.analysis_service import run_analysis
from face_analysis.models import FullAnalysisResult

class TestAnalysisService(unittest.IsolatedAsyncioTestCase):

    @patch('bot.services.analysis_service.validate_image')
    @patch('bot.services.analysis_service.get_landmarks')
    @patch('bot.services.analysis_service.analyze_face')
    @patch('bot.services.analysis_service.build_report')
    async def test_run_analysis_success(self, mock_build_report, mock_analyze, mock_get_landmarks, mock_validate):
        # We need to ensure that the mocked functions behave correctly when run_in_executor is called.
        # Since run_in_executor runs in a separate thread, but we mock the underlying function, we just need to return values.
        
        mock_validate.return_value = (True, "")
        mock_get_landmarks.return_value = MagicMock()
        
        result_mock = MagicMock(spec=FullAnalysisResult)
        mock_analyze.return_value = result_mock
        
        mock_build_report.return_value = "report.pdf"
        
        final_pdf_path, analysis_result = await run_analysis("photo.jpg", "male", "output.pdf")
        
        self.assertEqual(final_pdf_path, "report.pdf")
        self.assertEqual(analysis_result, result_mock)

    @patch('bot.services.analysis_service.validate_image')
    async def test_run_analysis_invalid_image(self, mock_validate):
        mock_validate.return_value = (False, "too_blurry")
        
        with self.assertRaises(ValueError) as context:
            await run_analysis("photo.jpg", "male", "output.pdf")
            
        self.assertIn("Image validation failed: too_blurry", str(context.exception))

if __name__ == '__main__':
    unittest.main()
