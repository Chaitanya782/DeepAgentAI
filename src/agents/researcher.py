# src/agents/researcher.py
from typing import Dict, List, Any, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
from src.tools.tavily_search import TavilySearchTool
from src.tools.web_crawler import WebCrawler

load_dotenv()


class ResearcherAgent:
    """
    An agent responsible for conducting research and collecting data.
    """

    def __init__(self):
        # Set up Google API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Configure the Gemini model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

        # Initialize tools
        self.search_tool = TavilySearchTool()
        self.web_crawler = WebCrawler()

    def _generate_search_queries(self, topic: str, num_queries: int = 3) -> List[str]:
        """
        Generate search queries based on the research topic.

        Args:
            topic: The main research topic
            num_queries: Number of queries to generate

        Returns:
            List of search queries
        """
        prompt = f"""
        Given the research topic: "{topic}"

        Generate {num_queries} specific search queries that would help gather comprehensive information on this topic.
        Each query should:
        1. Focus on a different aspect of the topic
        2. Be specific enough to yield relevant results
        3. Be phrased as an actual search query (not a question)

        Format your response as a Python list of strings. Example: ["query 1", "query 2", "query 3"]
        """

        response = self.model.generate_content(prompt)

        try:
            # Extract the list of queries from the response
            response_text = response.text
            # Clean up the response to extract just the list
            if "[" in response_text and "]" in response_text:
                queries_str = response_text[response_text.find("["):response_text.rfind("]") + 1]
                # Convert string representation of list to actual list
                queries = eval(queries_str)
                return queries[:num_queries]  # Ensure we have the right number
            else:
                # Fallback if parsing fails
                lines = response_text.strip().split("\n")
                queries = [line.strip().strip('"\'') for line in lines if line.strip()]
                return queries[:num_queries]
        except Exception as e:
            print(f"Error parsing queries: {e}")
            # Return a default query if parsing fails
            return [f"comprehensive information about {topic}"]

    def _extract_relevant_info(self, sources: List[Dict[str, str]], topic: str) -> Dict[str, Any]:
        """
        Extract and summarize relevant information from sources.

        Args:
            sources: List of sources with title, url and content
            topic: The research topic

        Returns:
            Dictionary with extracted information
        """
        # Combine all source content for analysis
        combined_content = "\n\n".join([
            f"Source: {source['title']}\nURL: {source['url']}\n{source['content'][:1000]}..."
            for source in sources
        ])

        prompt = f"""
        Research Topic: {topic}

        Below are excerpts from various sources. Extract the most relevant information related to the research topic.

        {combined_content}

        Extract and organize the key information as follows:
        1. Main findings (3-5 key points)
        2. Important data or statistics
        3. Different perspectives or approaches
        4. Gaps in information that need further research

        Present this as structured JSON with these keys: "main_findings", "data_points", "perspectives", "information_gaps"
        """

        response = self.model.generate_content(prompt)

        try:
            # Parse the JSON response
            import json
            import re

            # Look for JSON-like content in the response
            response_text = response.text
            # Find content between curly braces
            json_match = re.search(r'\{.+\}', response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(0)
                # Clean up any markdown formatting
                json_str = json_str.replace('```json', '').replace('```', '')
                extracted_info = json.loads(json_str)
            else:
                # Fallback structure if JSON parsing fails
                extracted_info = {
                    "main_findings": [line.strip() for line in response_text.split("\n") if line.strip()],
                    "data_points": [],
                    "perspectives": [],
                    "information_gaps": []
                }

            return extracted_info

        except Exception as e:
            print(f"Error extracting information: {e}")
            # Return a basic structure if parsing fails
            return {
                "main_findings": ["Information extraction failed"],
                "data_points": [],
                "perspectives": [],
                "information_gaps": ["Complete information could not be extracted"]
            }

    def research(self, topic: str, depth: str = "basic") -> Dict[str, Any]:
        """
        Perform comprehensive research on a topic.

        Args:
            topic: The research topic
            depth: Research depth (basic, advanced)

        Returns:
            Dictionary containing research results
        """
        research_results = {
            "topic": topic,
            "queries": [],
            "sources": [],
            "extracted_info": {},
            "summary": ""
        }

        # Generate search queries
        queries = self._generate_search_queries(topic)
        research_results["queries"] = queries

        # Collect sources from all queries
        all_sources = []
        for query in queries:
            # Search using Tavily
            sources = self.search_tool.get_sources(query)

            # Track which query found which sources
            for source in sources:
                source["query"] = query
                all_sources.append(source)

        # Deduplicate sources based on URL
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            if source["url"] not in seen_urls:
                seen_urls.add(source["url"])
                unique_sources.append(source)

        research_results["sources"] = unique_sources

        # Extract relevant information
        if unique_sources:
            research_results["extracted_info"] = self._extract_relevant_info(unique_sources, topic)

        # Generate a research summary
        if unique_sources and research_results["extracted_info"]:
            extracted = research_results["extracted_info"]
            summary_prompt = f"""
            Research Topic: {topic}

            Main Findings:
            {', '.join(extracted.get('main_findings', []))}

            Data Points:
            {', '.join(extracted.get('data_points', []))}

            Different Perspectives:
            {', '.join(extracted.get('perspectives', []))}

            Information Gaps:
            {', '.join(extracted.get('information_gaps', []))}

            Based on the above information, provide a concise research summary (about 250 words) that synthesizes what we know about this topic.
            """

            summary_response = self.model.generate_content(summary_prompt)
            research_results["summary"] = summary_response.text

        return research_results