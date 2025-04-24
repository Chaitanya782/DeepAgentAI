# src/agents/drafter.py
from typing import Dict, List, Any
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class DrafterAgent:
    """
    An agent responsible for drafting answers and responses based on research data.
    """

    def __init__(self):
        # Set up Google API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Configure the Gemini model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

    def _format_research_data(self, research_data: Dict[str, Any]) -> str:
        """
        Format research data into a structured text for the model.

        Args:
            research_data: The research data from the researcher agent

        Returns:
            Formatted text representation of the research data
        """
        topic = research_data.get("topic", "Unknown Topic")
        queries = research_data.get("queries", [])
        sources = research_data.get("sources", [])
        extracted_info = research_data.get("extracted_info", {})
        summary = research_data.get("summary", "")

        formatted_text = f"# Research Data on: {topic}\n\n"

        # Add search queries
        formatted_text += "## Search Queries Used\n"
        for query in queries:
            formatted_text += f"- {query}\n"

        # Add summary if available
        if summary:
            formatted_text += f"\n## Research Summary\n{summary}\n"

        # Add extracted information
        if extracted_info:
            formatted_text += "\n## Key Findings\n"

            main_findings = extracted_info.get("main_findings", [])
            if main_findings:
                formatted_text += "### Main Points\n"
                for finding in main_findings:
                    formatted_text += f"- {finding}\n"

            data_points = extracted_info.get("data_points", [])
            if data_points:
                formatted_text += "\n### Important Data\n"
                for point in data_points:
                    formatted_text += f"- {point}\n"

            perspectives = extracted_info.get("perspectives", [])
            if perspectives:
                formatted_text += "\n### Different Perspectives\n"
                for perspective in perspectives:
                    formatted_text += f"- {perspective}\n"

            gaps = extracted_info.get("information_gaps", [])
            if gaps:
                formatted_text += "\n### Information Gaps\n"
                for gap in gaps:
                    formatted_text += f"- {gap}\n"

        # Add sources
        formatted_text += "\n## Sources\n"
        for i, source in enumerate(sources, 1):
            formatted_text += f"{i}. [{source.get('title', 'Untitled')}]({source.get('url', '')})\n"

        return formatted_text

    def draft_answer(self, research_data: Dict[str, Any], output_format: str = "markdown") -> Dict[str, Any]:
        """
        Draft a comprehensive answer based on research data.

        Args:
            research_data: The research data from the researcher agent
            output_format: The desired output format (markdown, plain_text, etc.)

        Returns:
            Dictionary containing the drafted answer and metadata
        """
        # Format the research data
        formatted_research = self._format_research_data(research_data)

        # Create prompt for the model
        topic = research_data.get("topic", "Unknown Topic")
        prompt = f"""
        You are an expert at drafting comprehensive, well-structured answers based on research data.

        RESEARCH TOPIC: {topic}

        RESEARCH DATA:
        {formatted_research}

        Your task:
        1. Draft a comprehensive answer on this topic using ONLY the information provided
        2. Structure your answer with clear sections and headings
        3. Include relevant information from the sources but synthesize it into a cohesive whole
        4. Highlight important data points, statistics, or findings
        5. Acknowledge different perspectives if present
        6. Mention any significant information gaps
        7. Include a "References" section at the end listing the sources used

        Format your response in {output_format}.
        """

        # Generate the answer
        response = self.model.generate_content(prompt)

        # Return the drafted answer with metadata
        result = {
            "topic": topic,
            "answer": response.text,
            "format": output_format,
            "sources_count": len(research_data.get("sources", [])),
            "source_urls": [source.get("url") for source in research_data.get("sources", [])]
        }

        return result

    def refine_answer(self, draft_answer: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Refine a drafted answer based on feedback.

        Args:
            draft_answer: The draft answer to refine
            feedback: Feedback for improvement

        Returns:
            Dictionary containing the refined answer and metadata
        """
        topic = draft_answer.get("topic", "Unknown Topic")
        original_answer = draft_answer.get("answer", "")
        output_format = draft_answer.get("format", "markdown")

        prompt = f"""
        You are an expert at refining and improving drafted answers.

        TOPIC: {topic}

        ORIGINAL DRAFT:
        {original_answer}

        FEEDBACK FOR IMPROVEMENT:
        {feedback}

        Your task:
        1. Carefully analyze the feedback provided
        2. Revise and improve the original draft based on this feedback
        3. Maintain the overall structure and content accuracy
        4. Make the improvements requested in the feedback
        5. Ensure the revised answer is well-organized and comprehensive

        Format your response in {output_format}.
        """

        # Generate the refined answer
        response = self.model.generate_content(prompt)

        # Update the draft answer with the refined version
        refined_answer = draft_answer.copy()
        refined_answer["answer"] = response.text
        refined_answer["refined"] = True
        refined_answer["feedback"] = feedback

        return refined_answer