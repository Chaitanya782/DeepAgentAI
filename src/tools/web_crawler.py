# src/tools/web_crawler.py
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import time
import random


class WebCrawler:
    """
    A web crawler tool to extract information from websites.
    """

    def __init__(self):
        # Set up a session for making requests
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_page(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetches a web page and returns its content.

        Args:
            url: The URL to fetch

        Returns:
            Tuple of (title, content) if successful, (None, None) otherwise
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Raise exception for 4XX/5XX status codes

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else "No title found"

            # Extract main content (this is a simple approach; actual implementation may vary)
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # Get text content
            content = soup.get_text(separator=' ', strip=True)

            # Clean up the content a bit
            content = ' '.join(content.split())

            return title, content

        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None, None

    def crawl_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Crawl a list of URLs and extract content from each.

        Args:
            urls: List of URLs to crawl

        Returns:
            List of dictionaries containing url, title, and content
        """
        results = []

        for url in urls:
            # Add a small delay to avoid overwhelming servers
            time.sleep(random.uniform(1.0, 3.0))

            title, content = self.fetch_page(url)

            if title and content:
                results.append({
                    "url": url,
                    "title": title,
                    "content": content[:10000]  # Limit content length
                })

        return results