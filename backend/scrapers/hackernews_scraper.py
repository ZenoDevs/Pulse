"""
Hacker News Scraper
"""
import time
import requests
from datetime import datetime
from typing import Optional
import pandas as pd
from .base_scraper import BaseScraper


class HackerNewsScraper(BaseScraper):
    """Scraper per Hacker News via Algolia API"""
    
    def __init__(self):
        super().__init__("hackernews")
        self.api_url = "https://hn.algolia.com/api/v1/search"
    
    def scrape(
        self,
        query: str,
        max_pages: int = 5,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Scraping Hacker News"""
        
        keywords = query.split('+')
        combined_query = " ".join(keywords)
        
        all_items = []
        
        try:
            for page in range(max_pages):
                params = {
                    'query': combined_query,
                    'tags': 'story',
                    'page': page
                }
                
                response = requests.get(self.api_url, params=params, timeout=30)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                hits = data.get('hits', [])
                
                if not hits:
                    break
                
                for hit in hits:
                    item = self._process_hit(hit)
                    if item:
                        all_items.append(item)
                
                time.sleep(1)  # Rate limiting
            
            df = pd.DataFrame(all_items)
            
            if not df.empty:
                df = self.normalize_output(df)
                df = self.validate_dates(df, start_date, end_date)
            
            return df
            
        except Exception as e:
            print(f"HackerNews scraper error: {e}")
            return pd.DataFrame()
    
    def _process_hit(self, hit: dict) -> Optional[dict]:
        """Processa un hit da HN"""
        
        title = hit.get('title', '')
        story_text = hit.get('story_text', '')
        created_at = hit.get('created_at', '')
        object_id = hit.get('objectID', '')
        points = hit.get('points', 0)
        
        # Parse data
        published_at = None
        if created_at:
            try:
                # ISO format: "2019-03-13T10:20:44Z"
                created_at_clean = created_at.replace("Z", "")
                published_at = datetime.strptime(created_at_clean, "%Y-%m-%dT%H:%M:%S")
            except Exception:
                pass
        
        return {
            'title': title,
            'content': story_text,
            'published_at': published_at,
            'source_id': object_id,
            'url': f"https://news.ycombinator.com/item?id={object_id}",
            'metadata': {
                'points': points
            }
        }
