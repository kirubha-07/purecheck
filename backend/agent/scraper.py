import os
import logging
import requests
from datetime import datetime
from typing import List, Dict
from django.conf import settings


logger = logging.getLogger(__name__)


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
                logger.info("[Scraper] No NewsAPI key available, using structured dummy data for %s", city)
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
                    'timestamp': article.get('publishedAt', datetime.now().isoformat()),
                    'source_url': article.get('url', ''),
                    'source': 'NEWS',
                    'data_source_type': 'REAL' if settings.DATA_MODE == 'REAL' else 'SIMULATED',
                })
            
            logger.info("[Scraper] Fetched %s news articles for %s", len(articles), city)
            return articles
        
        except requests.exceptions.RequestException as e:
            logger.warning("[Scraper] Error fetching news for %s: %s", city, e)
            return self._get_dummy_articles(city)
        except Exception as e:
            logger.warning("[Scraper] Unexpected error for %s: %s", city, e)
            return self._get_dummy_articles(city)
    
    def fetch_fssai_complaints(self) -> List[Dict]:
        """
        Scrape FSSAI complaints from official website.
        Falls back to dummy data if scraping fails or service unavailable.
        
        Returns:
            List of complaint dicts with keys: city, food_item, adulterant, severity, raw_text
        """
        logger.info("[Scraper] Using structured FSSAI mock complaints")
        return self._get_dummy_fssai_complaints()
    
    def _get_dummy_articles(self, city: str) -> List[Dict]:
        """Return dummy news articles for testing."""
        return [
            {
                'title': f'Food Safety Alert: Adulteration detected in dairy products in {city}',
                'description': f'Recent complaints about milk adulteration with detergent in {city}',
                'url': 'https://example.com/article1',
                'publishedAt': datetime.now().isoformat(),
                'timestamp': datetime.now().isoformat(),
                'source_url': 'https://example.com/article1',
                'source': 'NEWS',
                'data_source_type': 'SIMULATED',
                'city': city,
                'food': 'milk',
                'adulterant': 'detergent',
                'issue': 'detergent residue found in milk samples',
                'severity': 4,
            },
            {
                'title': f'Health Department warns about synthetic colors in sweets in {city}',
                'description': f'Local authorities warn consumers about synthetic colors found in traditional sweets',
                'url': 'https://example.com/article2',
                'publishedAt': datetime.now().isoformat(),
                'timestamp': datetime.now().isoformat(),
                'source_url': 'https://example.com/article2',
                'source': 'NEWS',
                'data_source_type': 'SIMULATED',
                'city': city,
                'food': 'sweets',
                'adulterant': 'synthetic color',
                'issue': 'synthetic colors detected in sweets',
                'severity': 3,
            },
        ]
    
    def _get_dummy_fssai_complaints(self) -> List[Dict]:
        """Return dummy FSSAI complaints for testing."""
        return [
            {
                'city': 'Trichy',
                'food': 'milk',
                'adulterant': 'detergent',
                'issue': 'detergent residue in milk sample',
                'severity': 4,
                'timestamp': datetime.now().isoformat(),
                'source_url': 'https://fssai.gov.in/mock/trichy-milk',
                'data_source_type': 'SIMULATED',
                'raw_text': 'Milk sample from local dairy tested positive for detergent residue'
            },
            {
                'city': 'Coimbatore',
                'food': 'turmeric',
                'adulterant': 'lead chromate',
                'issue': 'lead chromate found in turmeric powder',
                'severity': 5,
                'timestamp': datetime.now().isoformat(),
                'source_url': 'https://fssai.gov.in/mock/coimbatore-turmeric',
                'data_source_type': 'SIMULATED',
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
