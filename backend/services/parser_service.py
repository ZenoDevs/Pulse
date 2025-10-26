"""
Parser and Normalizer Service
Standardizes scraped articles before database storage
"""
import re
from datetime import datetime
from typing import List, Optional, Dict
import pandas as pd
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from models import ArticleCreate


class ParserService:
    """Service for parsing and normalizing article data"""
    
    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags and clean text"""
        if not text:
            return ""
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'"àèéìòùÀÈÉÌÒÙäöüÄÖÜßñÑ]', '', text)
        
        return text.strip()
    
    @staticmethod
    def normalize_date(date_input) -> Optional[datetime]:
        """
        Normalize various date formats to datetime object
        
        Args:
            date_input: Can be datetime, string, or None
        
        Returns:
            datetime object or None
        """
        if date_input is None:
            return None
        
        # Already datetime
        if isinstance(date_input, datetime):
            return date_input
        
        # String to datetime
        if isinstance(date_input, str):
            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%d.%m.%Y, %H:%M",
                "%Y-%m-%d",
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_input, fmt)
                except ValueError:
                    continue
            
            # Try pandas parsing as fallback
            try:
                return pd.to_datetime(date_input)
            except:
                pass
        
        return None
    
    @staticmethod
    def extract_metadata(raw_article: Dict, source: str) -> Dict:
        """
        Extract and structure metadata from raw article
        
        Args:
            raw_article: Raw article dict from scraper
            source: Source name (ansa, reddit, hackernews)
        
        Returns:
            Structured metadata dict
        """
        metadata = raw_article.get('metadata', {})
        
        # Source-specific metadata handling
        if source == 'reddit':
            return {
                'author': metadata.get('author', 'unknown'),
                'score': metadata.get('score', 0),
                'upvotes': metadata.get('upvotes', 0),
                'word_count': metadata.get('word_count', 0),
                'subreddit': 'italy',
            }
        elif source == 'hackernews':
            return {
                'points': metadata.get('points', 0),
                'item_type': 'story',
            }
        elif source == 'ansa':
            return {
                'section': metadata.get('section', 'news'),
            }
        
        return metadata
    
    @staticmethod
    def normalize_article(raw_article: Dict, source: str) -> ArticleCreate:
        """
        Normalize a raw article into ArticleCreate model
        
        Args:
            raw_article: Dict with keys: title, content, published_at, url, source_id, metadata
            source: Source name
        
        Returns:
            ArticleCreate instance ready for DB insertion
        """
        # Clean text fields
        title = ParserService.clean_html(raw_article.get('title', ''))
        content = ParserService.clean_html(raw_article.get('content', ''))
        
        # Normalize date
        published_at = ParserService.normalize_date(
            raw_article.get('published_at')
        )
        
        # Extract metadata
        raw_metadata = ParserService.extract_metadata(raw_article, source)
        
        # Create ArticleCreate instance
        return ArticleCreate(
            source=source,
            source_id=raw_article.get('source_id', ''),
            title=title,
            content=content,
            url=raw_article.get('url'),
            published_at=published_at,
            raw_metadata=raw_metadata
        )
    
    @staticmethod
    def similarity_ratio(text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    @staticmethod
    def deduplicate_articles(
        articles: List[ArticleCreate],
        similarity_threshold: float = 0.85
    ) -> List[ArticleCreate]:
        """
        Remove duplicate articles based on title similarity
        
        Args:
            articles: List of ArticleCreate instances
            similarity_threshold: Threshold for considering articles duplicates (0-1)
        
        Returns:
            List of unique articles
        """
        if not articles:
            return []
        
        unique_articles = []
        seen_titles = []
        
        for article in articles:
            is_duplicate = False
            
            for seen_title in seen_titles:
                similarity = ParserService.similarity_ratio(
                    article.title,
                    seen_title
                )
                
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.append(article.title)
        
        return unique_articles
    
    @staticmethod
    def parse_dataframe(
        df: pd.DataFrame
    ) -> List[ArticleCreate]:
        """
        Parse entire DataFrame from scraper into list of ArticleCreate
        
        Args:
            df: DataFrame from scraper with normalized columns (including 'source')
        
        Returns:
            List of parsed and normalized ArticleCreate instances
        """
        articles = []
        
        for _, row in df.iterrows():
            try:
                source = row.get('source', 'unknown')
                
                raw_article = {
                    'title': row.get('title', ''),
                    'content': row.get('content', ''),
                    'published_at': row.get('published_at'),
                    'url': row.get('url', ''),
                    'source_id': row.get('source_id', ''),
                    'metadata': row.get('metadata', {})
                }
                
                article = ParserService.normalize_article(raw_article, source)
                articles.append(article)
                
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
        
        return articles


# Singleton instance
parser_service = ParserService()
