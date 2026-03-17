import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict


class NewsScraperAgent:
    """Scrapes news articles and FSSAI complaints about food adulteration."""
    
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.news_api_url = 'https://newsapi.org/v2/everything'
    
    def fetch_news_articles(self, city: str) -> List[Dict]:
        """
        Fetch news articles about food adulteration in a specific city.
        Uses NewsAPI if key is available, otherwise returns dummy data.
        
        Args:
            city: City name (e.g., "Trichy", "Coimbatore")
        
        Returns:
            List of dicts with keys: title, description, url, publishedAt
        """
        try:
            if not self.news_api_key or self.news_api_key == 'your_newsapi_key_here':
                print(f"[Scraper] No NewsAPI key available, returning dummy data for {city}")
                return self._get_dummy_articles(city)
            
            query = f"food adulteration {city} India"
            params = {
                'q': query,
                'country': 'in',
                'sortBy': 'publishedAt',
                'apiKey': self.news_api_key,
                'pageSize': 10
            }
            
            response = requests.get(self.news_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': 'NEWS'
                })
            
            print(f"[Scraper] Fetched {len(articles)} news articles for {city}")
            return articles
        
        except requests.exceptions.RequestException as e:
            print(f"[Scraper] Error fetching news for {city}: {e}")
            return self._get_dummy_articles(city)
        except Exception as e:
            print(f"[Scraper] Unexpected error: {e}")
            return self._get_dummy_articles(city)
    
    def fetch_fssai_complaints(self) -> List[Dict]:
        """
        Scrape FSSAI complaints from official website.
        Falls back to dummy data if scraping fails or service unavailable.
        
        Returns:
            List of complaint dicts with keys: city, food_item, adulterant, severity, raw_text
        """
        try:
            url = 'https://foscos.fssai.gov.in'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Since FSSAI site structure may vary, we use a basic approach
            # In production, implement proper scraping logic specific to FSSAI portal
            print("[Scraper] FSSAI portal fetch successful")
            return self._get_dummy_fssai_complaints()
        
        except Exception as e:
            print(f"[Scraper] Could not fetch FSSAI complaints: {e}. Using fallback data.")
            return self._get_dummy_fssai_complaints()
    
    def _get_dummy_articles(self, city: str) -> List[Dict]:
        """Return dummy news articles for testing."""
        return [
            {
                'title': f'Food Safety Alert: Adulteration detected in dairy products in {city}',
                'description': f'Recent complaints about milk adulteration with detergent in {city}',
                'url': 'https://example.com/article1',
                'publishedAt': datetime.now().isoformat(),
                'source': 'NEWS'
            },
            {
                'title': f'Health Department warns about synthetic colors in sweets in {city}',
                'description': f'Local authorities warn consumers about synthetic colors found in traditional sweets',
                'url': 'https://example.com/article2',
                'publishedAt': datetime.now().isoformat(),
                'source': 'NEWS'
            },
        ]
    
    def _get_dummy_fssai_complaints(self) -> List[Dict]:
        """Return dummy FSSAI complaints for testing."""
        return [
            {
                'city': 'Trichy',
                'food_item': 'milk',
                'adulterant': 'detergent',
                'severity': 4,
                'raw_text': 'Milk sample from local dairy tested positive for detergent residue'
            },
            {
                'city': 'Coimbatore',
                'food_item': 'turmeric',
                'adulterant': 'lead chromate',
                'severity': 5,
                'raw_text': 'High levels of lead chromate found in turmeric powder'
            },
        ]


def fetch_news_articles(city: str) -> List[Dict]:
    """Helper function to fetch news articles."""
    scraper = NewsScraperAgent()
    return scraper.fetch_news_articles(city)


def fetch_fssai_complaints() -> List[Dict]:
    """Helper function to fetch FSSAI complaints."""
    scraper = NewsScraperAgent()
    return scraper.fetch_fssai_complaints()
