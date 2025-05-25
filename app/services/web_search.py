import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from app.utils.config import settings
from app.utils.logger import logger


class WebSearchService:
    def __init__(self):
        self.search_api_key = settings.search_api_key
        self.search_engine_id = settings.search_engine_id

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        try:
            # Using Google Custom Search API if available
            if self.search_api_key and self.search_engine_id:
                return await self._google_search(query, num_results)
            else:
                # Fallback to DuckDuckGo search
                return await self._duckduckgo_search(query, num_results)
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return []

    async def _google_search(self, query: str, num_results: int) -> List[Dict]:
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
        return []

    async def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict]:
        # Simplified DuckDuckGo search implementation
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = []

                for result in soup.find_all('div', class_='result')[:num_results]:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')

                    if title_elem:
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'link': title_elem.get('href', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                        })

                return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")

        return []


web_search_service = WebSearchService()
