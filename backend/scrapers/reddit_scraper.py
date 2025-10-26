"""
Reddit Scraper - adattato dal codice esistente
"""
import praw
from datetime import datetime
from typing import Optional
import pandas as pd
from .base_scraper import BaseScraper
from config import settings


class RedditScraper(BaseScraper):
    """Scraper per Reddit"""
    
    def __init__(self):
        super().__init__("reddit")
        
        # Inizializza PRAW
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID or "dummy",
            client_secret=settings.REDDIT_CLIENT_SECRET or "dummy",
            user_agent=settings.REDDIT_USER_AGENT
        )
        
        self.subreddit_name = "italy"
        self.min_upvotes = 25
        self.max_words = 500
    
    def scrape(
        self,
        query: str,
        max_pages: int = 5,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Scraping Reddit"""
        
        time_filter = self._get_time_filter(start_date, end_date)
        keywords = query.split('+')
        
        all_rows = []
        
        try:
            # 1) Ricerca combinata
            combined_query = " ".join(keywords)
            results = self.reddit.subreddit(self.subreddit_name).search(
                query=combined_query,
                sort="top",
                time_filter=time_filter,
                limit=max_pages * 100
            )
            
            for submission in results:
                row = self._process_submission(submission, combined_query)
                if row:
                    all_rows.append(row)
            
            # 2) Ricerche singole per prime 2 keyword
            if len(keywords) >= 2:
                for kw in keywords[:2]:
                    results = self.reddit.subreddit(self.subreddit_name).search(
                        query=kw,
                        sort="top",
                        time_filter=time_filter,
                        limit=max_pages * 100
                    )
                    
                    for submission in results:
                        row = self._process_submission(submission, kw)
                        if row:
                            all_rows.append(row)
            
            df = pd.DataFrame(all_rows)
            
            if not df.empty:
                # Rimuovi duplicati
                df.drop_duplicates(subset=['source_id'], inplace=True)
                
                # Normalizza
                df = self.normalize_output(df)
                df = self.validate_dates(df, start_date, end_date)
            
            return df
            
        except Exception as e:
            print(f"Reddit scraper error: {e}")
            return pd.DataFrame()
    
    def _process_submission(self, submission, searched_keyword: str) -> Optional[dict]:
        """Processa una submission Reddit"""
        
        if submission.ups < self.min_upvotes:
            return None
        
        title = submission.title or ""
        text = submission.selftext or ""
        combined_text = f"{title} {text}"
        word_count = len(combined_text.split())
        
        if word_count > self.max_words:
            return None
        
        return {
            'searched_keyword': searched_keyword,
            'title': title,
            'content': text,
            'published_at': datetime.fromtimestamp(submission.created_utc),
            'source_id': submission.id,
            'url': f"https://reddit.com{submission.permalink}",
            'metadata': {
                'author': submission.author.name if submission.author else "deleted",
                'score': submission.score,
                'upvotes': submission.ups,
                'word_count': word_count
            }
        }
    
    def _get_time_filter(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> str:
        """Determina time_filter per Reddit"""
        if not start_date or not end_date:
            return "all"
        
        delta_days = (end_date - start_date).days
        
        if delta_days <= 1:
            return "day"
        elif delta_days <= 7:
            return "week"
        elif delta_days <= 31:
            return "month"
        elif delta_days <= 365:
            return "year"
        else:
            return "all"
