# src/agents/coordinator.py
from typing import Dict, List, Any, Tuple
import os
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_core.messages import HumanMessage, AIMessage
import langgraph.graph as lg
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from typing import TypedDict
from .researcher import ResearcherAgent
from .drafter import DrafterAgent

load_dotenv()


class ResearchCoordinator:
    """
    Coordinator that orchestrates the research process using LangGraph.
    """

    def __init__(self):
        # Initialize agents
        self.researcher = ResearcherAgent()
        self.drafter = DrafterAgent()

        # Set up Google API for analysis
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Configure the Gemini model for coordination
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

        # Create the research workflow graph
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """
        Create the research workflow graph using LangGraph.

        Returns:
            LangGraph StateGraph representing the research workflow
        """

        # Define the state schema for our workflow
        class State(TypedDict):
            topic: str
            research_query: str
            research_results: Dict[str, Any]
            draft_answer: Dict[str, Any]
            feedback: str
            final_answer: Dict[str, Any]
            current_step: str
            complete: bool

        # Create the workflow graph
        workflow = StateGraph(State)

        # Define the nodes (steps) in our workflow

        # 1. Parse Query - Analyzes the user query and extracts the research topic
        def parse_query(state: State) -> State:
            query = state["research_query"]

            prompt = f"""
            Analyze the following research query and extract the main research topic or question:

            QUERY: {query}

            Provide just the main research topic as a concise phrase or question.
            """

            response = self.model.generate_content(prompt)
            topic = response.text.strip()

            return {"topic": topic, "current_step": "parse_query"}

        # 2. Conduct Research - Uses the researcher agent to gather information
        def conduct_research(state: State) -> State:
            topic = state["topic"]
            results = self.researcher.research(topic)

            return {"research_results": results, "current_step": "conduct_research"}

        # 3. Draft Answer - Uses the drafter agent to create an initial draft
        def draft_answer(state: State) -> State:
            research_results = state["research_results"]
            draft = self.drafter.draft_answer(research_results)

            return {"draft_answer": draft, "current_step": "draft_answer"}

        # 4. Analyze Draft - Analyzes the draft for quality and suggests improvements
        def analyze_draft(state: State) -> State:
            draft = state["draft_answer"]
            answer_text = draft.get("answer", "")
            topic = state["topic"]

            prompt = f"""
            Analyze the following drafted answer on the topic: "{topic}"

            DRAFT ANSWER:
            {answer_text[:2000]}... [truncated for brevity]

            Evaluate this draft and provide specific feedback for improvement in these areas:
            1. Content completeness and accuracy
            2. Structure and organization
            3. Clarity and readability
            4. Use of evidence and sources

            Provide concise, actionable feedback that can be used to improve the draft.
            """

            response = self.model.generate_content(prompt)
            feedback = response.text.strip()

            return {"feedback": feedback, "current_step": "analyze_draft"}

        # 5. Refine Answer - Refines the draft based on feedback
        def refine_answer(state: State) -> State:
            draft = state["draft_answer"]
            feedback = state["feedback"]

            refined = self.drafter.refine_answer(draft, feedback)

            return {"final_answer": refined, "current_step": "refine_answer", "complete": True}

        # Add all nodes to the graph
        workflow.add_node("parse_query", parse_query)
        workflow.add_node("conduct_research", conduct_research)
        workflow.add_node("generate_draft", draft_answer)
        workflow.add_node("analyze_draft", analyze_draft)
        workflow.add_node("refine_answer", refine_answer)

        # Define the edges (transitions) between nodes
        workflow.add_edge("parse_query", "conduct_research")
        workflow.add_edge("conduct_research", "generate_draft")
        workflow.add_edge("generate_draft", "analyze_draft")
        workflow.add_edge("analyze_draft", "refine_answer")
        workflow.add_edge("refine_answer", END)

        # Set the entry point
        workflow.set_entry_point("parse_query")

        # Compile the workflow
        return workflow.compile()

    def execute_research(self, query: str) -> Dict[str, Any]:
        """
        Execute the research process for a given query.

        Args:
            query: The research query or topic

        Returns:
            Dictionary containing the complete research results
        """
        # Initial state
        initial_state = {
            "topic": "",
            "research_query": query,
            "research_results": {},
            "draft_answer": {},
            "feedback": "",
            "final_answer": {},
            "current_step": "",
            "complete": False
        }

        # Execute the workflow
        results = {}
        for event in self.workflow.stream(initial_state):
            results = event
            print(f"Completed step: {results.get('current_step', 'unknown')}")

        return results