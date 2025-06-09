import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from app.utils.config import settings  # For config values like API keys
from app.utils.logger import logger  # To log info and errors


class WebSearchService:
    def __init__(self):
        """
        Initialize WebSearchService instance.

        Loads API key and search engine ID from settings config,
        which are required to use Google Custom Search API.

        If these are missing, service will fallback to DuckDuckGo scraping.
        """
        self.search_api_key = settings.search_api_key
        self.search_engine_id = settings.search_engine_id

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Public method to perform web search based on query and desired number of results.

        Logic:
        - If Google Custom Search API credentials are present, use Google API.
        - Otherwise, fallback to scraping DuckDuckGo HTML search results.
        - Handles any exceptions, logs errors, and returns empty list on failure.

        Args:
            query (str): Search term/query string.
            num_results (int): Number of results desired (default 5).

        Returns:
            List[Dict]: List of search results, each with 'title', 'link', and 'snippet'.
        """
        try:
            # Prefer Google Custom Search API if credentials are available
            if self.search_api_key and self.search_engine_id:
                return await self._google_search(query, num_results)
            else:
                # Use DuckDuckGo scraping fallback when Google API not configured
                return await self._duckduckgo_search(query, num_results)
        except Exception as e:
            # Log error but don't crash
            logger.error(f"Error in web search: {e}")
            return []

    async def _google_search(self, query: str, num_results: int) -> List[Dict]:
        """
        Performs a search using Google Custom Search API.

        Builds request URL and parameters with API key, search engine ID, query, and number of results.
        Sends HTTP GET request to Google's search endpoint.
        Parses JSON response and extracts relevant data (title, link, snippet) for each item.
        Returns empty list if response is not successful or data missing.

        Args:
            query (str): Search query string.
            num_results (int): Max number of results to fetch.

        Returns:
            List[Dict]: List of result dicts with 'title', 'link', 'snippet'.
        """
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.search_api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': num_results
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            return results
        # If API call failed or no data, return empty list
        return []

    async def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict]:
        """
        Simplified web scraping implementation for DuckDuckGo search results.

        Since DuckDuckGo does not offer a free official API like Google,
        this method scrapes the HTML page returned by a DuckDuckGo search query.

        Steps:
        - Build DuckDuckGo HTML search URL with the query.
        - Send GET request with a browser-like User-Agent header to avoid blocking.
        - Parse returned HTML content with BeautifulSoup.
        - Extract up to `num_results` search results by looking for specific HTML elements/classes.
        - For each result, extract title text, link URL, and snippet text (if available).
        - Return list of results dicts with title, link, and snippet.
        - Handles exceptions and logs any errors encountered.

        Args:
            query (str): Search query string.
            num_results (int): Number of results to fetch.

        Returns:
            List[Dict]: List of search result dictionaries.
        """
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {
            # Pretend to be a browser so the server doesn't block the request
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []

                # DuckDuckGo's HTML structure uses div.result for each result
                # We limit results to the requested number (num_results)
                for result in soup.find_all('div', class_='result')[:num_results]:
                    # Extract the <a> tag with class 'result__a' for the title and link
                    title_elem = result.find('a', class_='result__a')
                    # Extract snippet text from a <a> tag with class 'result__snippet', if available
                    snippet_elem = result.find('a', class_='result__snippet')

                    if title_elem:
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'link': title_elem.get('href', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                        })

                return results
        except Exception as e:
            # Log exceptions like request timeout, parsing errors, etc.
            logger.error(f"DuckDuckGo search error: {e}")

        # Return empty list if any failure occurs
        return []


# Singleton instance of WebSearchService for reuse across app
web_search_service = WebSearchService()
