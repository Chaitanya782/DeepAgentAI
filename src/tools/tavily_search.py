# src/tools/tavily_search.py
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


class TavilySearchTool:
    """
    A tool for performing web searches using the Tavily API.
    """

    def __init__(self):
        # Get API key from environment variables
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")

        # Initialize the Tavily client
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 5, search_depth: str = "basic") -> Dict[str, Any]:
        """
        Perform a search using Tavily API.

        Args:
            query: The search query
            max_results: Maximum number of results to return
            search_depth: How deep to search ("basic", "advanced")

        Returns:
            Dictionary containing search results and related information
        """
        try:
            # Perform the search using Tavily
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=True,
                include_raw_content=True,
                include_images=False
            )

            return response
        except Exception as e:
            print(f"Error during Tavily search: {e}")
            return {
                "query": query,
                "answer": None,
                "results": [],
                "error": str(e)
            }

    def get_sources(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Get just the sources from a search.

        Args:
            query: The search query
            max_results: Maximum number of results to return

        Returns:
            List of sources with title, url and content
        """
        response = self.search(query, max_results)

        sources = []
        if "results" in response:
            for result in response["results"]:
                sources.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", "")
                })

        return sources
