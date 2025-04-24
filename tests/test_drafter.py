# tests/test_drafter.py
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.drafter import DrafterAgent


class TestDrafter(unittest.TestCase):

    @patch('src.agents.drafter.genai')
    def test_draft_answer(self, mock_genai):
        # Setup mocks
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a drafted answer"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Create drafter agent
        drafter = DrafterAgent()

        # Create sample research data
        research_data = {
            "topic": "artificial intelligence",
            "queries": ["AI applications", "AI ethics"],
            "sources": [
                {"title": "AI Ethics", "url": "https://example.com/ethics", "content": "Ethics content"},
                {"title": "AI Applications", "url": "https://example.com/apps", "content": "Applications content"}
            ],
            "extracted_info": {
                "main_findings": ["Finding 1", "Finding 2"],
                "data_points": ["Data 1", "Data 2"],
                "perspectives": ["Perspective 1"],
                "information_gaps": ["Gap 1"]
            },
            "summary": "This is a summary"
        }

        # Test the method
        result = drafter.draft_answer(research_data)

        # Assert results
        self.assertEqual(result["topic"], "artificial intelligence")
        self.assertEqual(result["answer"], "This is a drafted answer")
        self.assertEqual(result["sources_count"], 2)

        # Verify method calls
        mock_model.generate_content.assert_called_once()

    @patch('src.agents.drafter.genai')
    def test_refine_answer(self, mock_genai):
        # Setup mocks
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a refined answer"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Create drafter agent
        drafter = DrafterAgent()

        # Create sample draft answer
        draft_answer = {
            "topic": "artificial intelligence",
            "answer": "This is the original draft",
            "format": "markdown",
            "sources_count": 2,
            "source_urls": ["https://example.com/1", "https://example.com/2"]
        }

        # Test the method
        feedback = "Improve the clarity and add more details"
        result = drafter.refine_answer(draft_answer, feedback)

        # Assert results
        self.assertEqual(result["topic"], "artificial intelligence")
        self.assertEqual(result["answer"], "This is a refined answer")
        self.assertTrue(result["refined"])
        self.assertEqual(result["feedback"], feedback)

        # Verify method calls
        mock_model.generate_content.assert_called_once()


if __name__ == '__main__':
    unittest.main()