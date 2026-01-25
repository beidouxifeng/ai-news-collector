import feedparser
import requests
from datetime import datetime, timezone
import time
import logging
from typing import List, Dict, Optional
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSFetcher:
    """RSS feed fetcher class"""
    
    def __init__(self, config_path: str = "config/rss_sources.json"):
        self.config_path = config_path
        self.sources = self._load_sources()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _load_sources(self) -> List[Dict]:
        """Load RSS sources from config file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return [s for s in config.get('sources', []) if s.get('enabled', True)]
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using default sources")
            return self._get_default_sources()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            return self._get_default_sources()
    
    def _get_default_sources(self) -> List[Dict]:
        """Get default RSS sources if config file not found"""
        return [
            {
                "name": "36氪",
                "url": "https://36kr.com/feed",
                "category": "科技媒体",
                "enabled": True,
                "language": "zh"
            },
            {
                "name": "虎嗅网",
                "url": "https://www.huxiu.com/rss/0.xml",
                "category": "科技媒体",
                "enabled": True,
                "language": "zh"
            },
            {
                "name": "少数派",
                "url": "https://sspai.com/feed",
                "category": "科技媒体",
                "enabled": True,
                "language": "zh"
            }
        ]
    
    def fetch_feed(self, source: Dict) -> List[Dict]:
        """Fetch articles from a single RSS feed"""
        url = source['url']
        source_name = source['name']
        articles = []
        
        try:
            logger.info(f"Fetching from {source_name}...")
            
            # Fetch with timeout
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {source_name}: {feed.bozo}")
            
            # Extract articles
            for entry in feed.entries:
                article = self._parse_entry(entry, source)
                if article:
                    articles.append(article)
            
            logger.info(f"✓ Fetched {len(articles)} articles from {source_name}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error fetching {source_name}: {e}")
        except Exception as e:
            logger.error(f"✗ Unexpected error processing {source_name}: {e}")
        
        return articles
    
    def _parse_entry(self, entry, source: Dict) -> Optional[Dict]:
        """Parse a single feed entry"""
        try:
            # Get publish date
            published = entry.get('published_parsed')
            if published:
                pub_date = datetime(*published[:6], tzinfo=timezone.utc)
            else:
                pub_date = datetime.now(timezone.utc)
            
            # Get content/description
            content = entry.get('content', [{}])[0].get('value') or \
                      entry.get('description', '') or \
                      entry.get('summary', '')
            
            # Clean HTML tags from content
            from bs4 import BeautifulSoup
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text(strip=True)
            
            # Get authors
            authors = []
            if hasattr(entry, 'author'):
                authors = [entry.author]
            elif hasattr(entry, 'authors'):
                authors = [author.get('name', '') for author in entry.authors]
            
            article = {
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', ''),
                'content': content[:5000],  # Limit content length
                'summary': content[:300],
                'published': pub_date,
                'source': source['name'],
                'source_category': source.get('category', 'Other'),
                'language': source.get('language', 'en'),
                'authors': authors,
                'tags': [tag.term for tag in entry.get('tags', [])]
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    def fetch_all(self, delay: float = 1.0) -> List[Dict]:
        """Fetch articles from all configured sources"""
        all_articles = []
        
        logger.info(f"Starting fetch from {len(self.sources)} sources...")
        
        for i, source in enumerate(self.sources):
            articles = self.fetch_feed(source)
            all_articles.extend(articles)
            
            # Add delay between requests to be polite
            if i < len(self.sources) - 1:
                time.sleep(delay)
        
        logger.info(f"✓ Total articles fetched: {len(all_articles)}")
        
        return all_articles
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title and link"""
        seen = set()
        unique_articles = []
        
        for article in articles:
            # Create a unique key from title and link
            key = (article['title'], article['link'])
            
            if key not in seen:
                seen.add(key)
                unique_articles.append(article)
            else:
                logger.debug(f"Duplicate removed: {article['title']}")
        
        logger.info(f"✓ After deduplication: {len(unique_articles)} unique articles")
        
        return unique_articles


def main():
    """Test the RSS fetcher"""
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()
    articles = fetcher.deduplicate(articles)
    
    print(f"\nFetched {len(articles)} unique articles")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   {article['source']} - {article['published']}")
        print(f"   {article['summary']}")


if __name__ == "__main__":
    main()
