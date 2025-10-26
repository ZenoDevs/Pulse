"""
Scraper Registry - gestisce tutti gli scraper disponibili
"""
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from .base_scraper import BaseScraper
from .ansa_scraper import AnsaScraper
from .reddit_scraper import RedditScraper
from .hackernews_scraper import HackerNewsScraper


class ScraperRegistry:
    """Registry di tutti gli scraper disponibili"""
    
    def __init__(self):
        self.scrapers: Dict[str, BaseScraper] = {
            'ansa': AnsaScraper(),
            'reddit': RedditScraper(),
            'hackernews': HackerNewsScraper(),
        }
    
    def get_scraper(self, source: str) -> Optional[BaseScraper]:
        """Ritorna lo scraper per una fonte specifica"""
        return self.scrapers.get(source.lower())
    
    def list_sources(self) -> List[str]:
        """Lista tutte le fonti disponibili"""
        return list(self.scrapers.keys())
    
    def scrape_all(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_pages: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Esegue scraping su multiple fonti e unisce i risultati
        
        Args:
            query: Query di ricerca
            sources: Lista fonti (None = tutte)
            max_pages: Pagine max per fonte
            start_date: Data inizio
            end_date: Data fine
        
        Returns:
            DataFrame unificato con tutti i risultati
        """
        if sources is None:
            sources = self.list_sources()
        
        all_results = []
        
        for source in sources:
            scraper = self.get_scraper(source)
            if not scraper:
                print(f"Warning: scraper '{source}' non trovato")
                continue
            
            print(f"Scraping {source}...")
            
            try:
                df = scraper.scrape(
                    query=query,
                    max_pages=max_pages,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not df.empty:
                    all_results.append(df)
                    print(f"  -> {len(df)} articoli da {source}")
                else:
                    print(f"  -> Nessun risultato da {source}")
                    
            except Exception as e:
                print(f"Errore scraping {source}: {e}")
        
        if not all_results:
            return pd.DataFrame()
        
        # Unisci tutti i risultati
        combined_df = pd.concat(all_results, ignore_index=True)
        
        # Rimuovi duplicati basati su source + source_id
        combined_df.drop_duplicates(
            subset=['source', 'source_id'],
            keep='first',
            inplace=True
        )
        
        print(f"\nTotale: {len(combined_df)} articoli unici")
        
        return combined_df


# Singleton instance
scraper_registry = ScraperRegistry()
