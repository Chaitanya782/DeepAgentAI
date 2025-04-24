# src/main.py
import argparse
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from src.agents.coordinator import ResearchCoordinator

def save_results(results, output_dir="./output"):
    """Save research results to a file."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create filename based on topic
    topic = results.get("topic", "research")
    topic_slug = topic.lower().replace(" ", "_")[:30]
    filename = f"{output_dir}/{timestamp}_{topic_slug}.json"

    # Save full results as JSON
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    # Also save the final answer as markdown
    # final_answer = results.get("final_answer", {}).get("answer", "")
    final_answer = results.get("refine_answer", {}).get("final_answer", {}).get("answer", "")

    md_filename = f"{output_dir}/{timestamp}_{topic_slug}.md"

    with open(md_filename, 'w') as f:
        f.write(final_answer)

    print(f"Results saved to {filename} and {md_filename}")
    return filename, md_filename


def main():
    """Main function to run the research system."""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Deep Research System')
    parser.add_argument('--query', '-q', type=str, help='Research query')
    parser.add_argument('--output', '-o', type=str, default='./output', help='Output directory')
    args = parser.parse_args()

    # Get query from arguments or prompt user
    query = args.query
    if not query:
        query = input("Enter your research query: ")

    print(f"Starting research on: {query}")

    # Initialize coordinator and execute research
    coordinator = ResearchCoordinator()
    results = coordinator.execute_research(query)

    # Save results
    save_results(results, args.output)

    # Print completion message
    print("\nResearch complete!")
    topic = results.get("topic", "")
    print(f"Topic: {topic}")

    sources_count = results.get("final_answer", {}).get("sources_count", 0)
    print(f"Sources analyzed: {sources_count}")

    print("\nFinal answer has been saved to the output directory.")


if __name__ == "__main__":
    main()