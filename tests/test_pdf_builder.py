import sys
import os

if sys.platform == 'darwin':
    os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('DYLD_FALLBACK_LIBRARY_PATH', '')

import unittest
from unittest.mock import patch, MagicMock
from report.pdf.builder import parse_ai_text

class TestPdfBuilder(unittest.TestCase):
    
    def test_parse_ai_text(self):
        raw_text = "Это первый абзац.\n\nЭто второй абзац.\n\n**ВЛИЯНИЕ:** Это влияние."
        body, influence = parse_ai_text(raw_text)
        
        self.assertIn("<p>Это первый абзац.</p>", body)
        self.assertIn("<p>Это второй абзац.</p>", body)
        self.assertEqual(influence, "Это влияние.")
        
    def test_parse_ai_text_no_influence(self):
        raw_text = "Это первый абзац.\n\nЭто второй абзац."
        body, influence = parse_ai_text(raw_text)
        
        self.assertIn("<p>Это первый абзац.</p>", body)
        self.assertEqual(influence, "Влияет на общее восприятие гармонии лица.")

if __name__ == '__main__':
    unittest.main()
