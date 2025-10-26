"""
Base scraper interface - tutti gli scraper devono implementare questa interfaccia
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
import pandas as pd


class BaseScraper(ABC):
    """Interfaccia base per tutti gli scraper"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    @abstractmethod
    def scrape(
        self,
        query: str,
        max_pages: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Esegue lo scraping
        
        Returns:
            DataFrame con colonne: Title, Text, Date, source_id, url, metadata
        """
        pass
    
    def normalize_output(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizza l'output in formato standard
        Aggiunge colonna 'source' e rinomina se necessario
        """
        if df.empty:
            return pd.DataFrame(columns=[
                'source', 'source_id', 'title', 'content', 
                'url', 'published_at', 'metadata'
            ])
        
        # Assicura colonne standard
        df = df.copy()
        df['source'] = self.source_name
        
        # Rinomina colonne comuni
        column_mapping = {
            'Title': 'title',
            'Text': 'content',
            'Date': 'published_at'
        }
        
        for old, new in column_mapping.items():
            if old in df.columns and new not in df.columns:
                df[new] = df[old]
        
        return df
    
    def validate_dates(
        self,
        df: pd.DataFrame,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Filtra DataFrame per range date"""
        if df.empty or 'published_at' not in df.columns:
            return df
        
        df = df.copy()
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        
        if start_date:
            df = df[df['published_at'] >= start_date]
        
        if end_date:
            df = df[df['published_at'] <= end_date]
        
        return df
