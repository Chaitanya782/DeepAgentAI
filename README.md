# AI Agent-Based Deep Research System

This project implements an advanced AI-powered deep research system that utilizes multiple agents working together to gather, analyze, and synthesize information from the web. It leverages the Tavily search API for intelligent web searches, and uses LangGraph & LangChain to coordinate multiple specialized AI agents.

## Features

- **Multi-Agent System**: Separate agents for research and content drafting, coordinated through LangGraph
- **Web Crawling & Information Gathering**: Utilizes Tavily API for high-quality search results and custom web crawling
- **Intelligent Processing**: Extracts relevant information, identifies key data points, perspectives, and gaps
- **Structured Research Workflow**: Follows a defined process from query parsing to final answer refinement
- **Quality Assurance**: Draft analysis and refinement ensures high-quality output
- **Modular Design**: Easy to extend with additional agent types or tools

## Architecture

The system is built around these core components:

1. **Researcher Agent**: Handles search query generation, web search, and data extraction
2. **Drafter Agent**: Creates well-structured answers based on research data 
3. **Research Coordinator**: Orchestrates the research workflow using LangGraph
4. **Tools**: 
   - Tavily Search Tool for intelligent web searches
   - Web Crawler for extracting content from URLs

## Installation

### Prerequisites

- Python 3.9+ 
- Tavily API key
- Google API key (for Gemini Pro)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ai-deep-research.git
   cd DeepAgentAI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   TAVILY_API_KEY=your_tavily_api_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Basic Usage

Run the system with a research query:

```bash
python -m src.main --"What are the current applications of quantum computing in healthcare?"
```

Or run it interactively:

```bash
python src/main.py
```

### Command Line Options

- `--query` or `-q`: Research query (if not provided, will prompt for input)
- `--output` or `-o`: Output directory for research results (default: `./output`)

## Output

The system generates two output files:
1. A JSON file with the complete research data, including sources and intermediate results
2. A Markdown file with the final answer, formatted and ready for use

## How It Works

1. **Query Parsing**: Analyzes the research query to extract the main topic
2. **Search Query Generation**: Creates targeted search queries to explore different aspects of the topic
3. **Information Gathering**: Uses Tavily to search the web and crawls relevant websites
4. **Information Extraction**: Identifies key information, data points, and different perspectives
5. **Draft Creation**: Synthesizes findings into a comprehensive, structured answer
6. **Quality Analysis**: Evaluates the draft and provides improvement feedback
7. **Refinement**: Enhances the draft based on feedback to create the final answer

## Extending the System

The modular design allows for easy extension:

- Add new agent types in the `agents` directory
- Implement additional search or analysis tools in the `tools` directory
- Modify the research workflow in `coordinator.py`

## Testing

Run tests with:

```bash
python -m unittest discover tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.