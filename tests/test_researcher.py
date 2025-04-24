# tests/test_researcher.py
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.researcher import ResearcherAgent


class TestResearcher(unittest.TestCase):

    @patch('src.agents.researcher.genai')
    @patch('src.agents.researcher.TavilySearchTool')
    def test_generate_search_queries(self, mock_tavily, mock_genai):
        # Setup mocks
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '["query 1", "query 2", "query 3"]'
        mock_model.generate_content.return_value = mock_response
        # tests/test_researcher.py (continued)
        mock_genai.GenerativeModel.return_value = mock_model

        # Create researcher agent
        researcher = ResearcherAgent()

        # Test the method
        queries = researcher._generate_search_queries("artificial intelligence")

        # Assert results
        self.assertEqual(len(queries), 3)
        self.assertEqual(queries[0], "query 1")
        self.assertEqual(queries[1], "query 2")
        self.assertEqual(queries[2], "query 3")

        # Verify method calls
        mock_model.generate_content.assert_called_once()

    @patch('src.agents.researcher.genai')
    @patch('src.agents.researcher.TavilySearchTool')
    @patch('src.agents.researcher.WebCrawler')
    def test_research_flow(self, mock_crawler, mock_tavily, mock_genai):
        # Setup mocks
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '["query 1", "query 2"]'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Setup tavily search tool mock
        mock_tavily_instance = MagicMock()
        mock_tavily_instance.get_sources.return_value = [
            {"title": "Test Title", "url": "https://example.com", "content": "Test content"}
        ]
        mock_tavily.return_value = mock_tavily_instance

        # Create researcher agent
        researcher = ResearcherAgent()

        # Test the research method
        result = researcher.research("artificial intelligence")

        # Assert results
        self.assertEqual(result["topic"], "artificial intelligence")
        self.assertIsInstance(result["queries"], list)
        self.assertIsInstance(result["sources"], list)

        # Verify method calls
        self.assertTrue(mock_tavily_instance.get_sources.called)
        self.assertTrue(mock_model.generate_content.called)


if __name__ == '__main__':
    unittest.main()