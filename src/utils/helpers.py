# src/utils/helpers.py
import os
import json
from typing import Dict, Any, List
from datetime import datetime
import re


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.

    Args:
        text: Input text to clean

    Returns:
        Cleaned text string
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def extract_key_points(text: str, num_points: int = 5) -> List[str]:
    """
    Extract key points from a longer text.
    Simple implementation based on sentence importance.

    Args:
        text: Input text to analyze
        num_points: Number of key points to extract

    Returns:
        List of extracted key points
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Simple scoring: longer sentences with keywords are more important
    keywords = ["important", "significant", "key", "major", "critical",
                "essential", "primary", "crucial", "vital", "fundamental"]

    scored_sentences = []
    for sentence in sentences:
        # Skip very short sentences
        if len(sentence.split()) < 5:
            continue

        # Calculate base score from length (normalized)
        score = min(1.0, len(sentence) / 200)

        # Add points for keywords
        for keyword in keywords:
            if keyword.lower() in sentence.lower():
                score += 0.2

        scored_sentences.append((sentence, score))

    # Sort by score and take top N
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    top_sentences = [s[0] for s in scored_sentences[:num_points]]

    return top_sentences


def save_research_data(data: Dict[str, Any], output_dir: str = "./output") -> str:
    """
    Save research data to a file.

    Args:
        data: Research data to save
        output_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_slug = data.get("topic", "research").lower().replace(" ", "_")[:30]
    filename = f"{output_dir}/{timestamp}_{topic_slug}.json"

    # Save to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filename


def load_research_data(filename: str) -> Dict[str, Any]:
    """
    Load research data from a file.

    Args:
        filename: Path to the file

    Returns:
        Loaded research data
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data