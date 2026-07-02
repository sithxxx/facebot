import unittest
from unittest.mock import patch, MagicMock
from report.text_generator import generate_metric_text, generate_overall_summary, generate_improvement_advice
from face_analysis.models import MetricResult, FullAnalysisResult

class TestTextGenerator(unittest.TestCase):

    @patch('report.text_generator.client.chat.completions.create')
    def test_generate_metric_text_success(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Paragraph 1\n\nParagraph 2\n\n**ВЛИЯНИЕ:** Impact."
        mock_create.return_value = mock_response
        
        metric = MetricResult(
            name="face_symmetry", name_ru="Симметрия", raw_value=0.5, norm_value=0.5,
            sigma_deviation=0.0, score=5.0, description="Desc"
        )
        
        result = generate_metric_text(metric, "male")
        self.assertIn("Paragraph 1", result)
        self.assertIn("ВЛИЯНИЕ", result)

    @patch('report.text_generator.client.chat.completions.create')
    def test_generate_metric_text_failure(self, mock_create):
        mock_create.side_effect = Exception("API Error")
        
        metric = MetricResult(
            name="face_symmetry", name_ru="Симметрия", raw_value=0.5, norm_value=0.5,
            sigma_deviation=0.0, score=5.0, description="Desc"
        )
        
        result = generate_metric_text(metric, "male")
        self.assertIn("ошибки сети", result)

    @patch('report.text_generator.client.chat.completions.create')
    def test_generate_advice_success(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '[{"metric_name_ru": "Губы", "category": "Стиль", "advice_text": "Тест"}]'
        mock_create.return_value = mock_response
        
        result_obj = FullAnalysisResult(
            metrics=[MetricResult(name="lip", name_ru="Губы", raw_value=0, norm_value=0, sigma_deviation=0, score=1.0, description="")],
            overall_score=5.0, top_strengths=[], top_weaknesses=[], gender="male"
        )
        
        advice = generate_improvement_advice(result_obj)
        self.assertEqual(len(advice), 1)
        self.assertEqual(advice[0]["metric_name_ru"], "Губы")

if __name__ == '__main__':
    unittest.main()
