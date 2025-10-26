"""
ANSA Scraper - adattato dal codice esistente
"""
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from typing import Optional
from .base_scraper import BaseScraper


def convert_ansa_date(raw_date_str: str) -> Optional[datetime]:
    """
    Converte stringhe ANSA tipo 'Rubriche- 25.12.2024, 11:44'
    in datetime
    """
    try:
        match = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4},\s*\d{1,2}:\d{2})", raw_date_str)
        if match:
            date_str = match.group(1)
            return datetime.strptime(date_str, "%d.%m.%Y, %H:%M")
        return None
    except Exception as e:
        print(f"Errore convert_ansa_date({raw_date_str}): {e}")
        return None


class AnsaScraper(BaseScraper):
    """Scraper per ANSA"""
    
    def __init__(self):
        super().__init__("ansa")
        self.base_url = "https://www.ansa.it/ricerca/ansait/search.shtml"
    
    def scrape(
        self,
        query: str,
        max_pages: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Scraping ANSA con gestione periodo"""
        
        # Determina periodo param
        period_param = self._get_period_param(start_date, end_date)
        
        titles = []
        texts = []
        dates = []
        urls = []
        
        page_number = 0
        
        try:
            while page_number < max_pages * 12:
                url = (
                    f"{self.base_url}"
                    f"?start={page_number}"
                    f"&tag=&any={query}"
                    "&sezione=&sort=data%3Adesc"
                    f"&periodo={period_param}"
                )
                
                response = requests.get(url, timeout=30)
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                title_elems = soup.find_all("h2", "title")
                text_elems = soup.find_all("div", "text")
                date_elems = soup.find_all("p", "meta")
                
                if not title_elems:
                    break
                
                for title in title_elems:
                    titles.append(title.get_text(strip=True))
                    # Estrai URL se presente
                    link = title.find_parent('a')
                    if link and link.get('href'):
                        urls.append(f"https://www.ansa.it{link['href']}")
                    else:
                        urls.append("")
                
                for text in text_elems:
                    texts.append(text.get_text(strip=True))
                
                for date_elem in date_elems:
                    dates.append(date_elem.get_text(strip=True))
                
                page_number += 12
            
            # Allinea lunghezze
            min_len = min(len(titles), len(texts), len(dates))
            
            df = pd.DataFrame({
                'Title': titles[:min_len],
                'Text': texts[:min_len],
                'Date': dates[:min_len],
                'url': urls[:min_len] if urls else [""] * min_len
            })
            
            # Converti date
            if not df.empty:
                df['Date'] = df['Date'].apply(convert_ansa_date)
                # Genera source_id: prima da URL, poi hash del titolo
                df['source_id'] = df.apply(
                    lambda row: (
                        row['url'].split('/')[-1] if row['url'] 
                        else f"ansa_{hash(row['Title'])}"
                    ),
                    axis=1
                )
            
            # Normalizza output
            df = self.normalize_output(df)
            df = self.validate_dates(df, start_date, end_date)
            
            return df
            
        except Exception as e:
            print(f"ANSA scraper error: {e}")
            return pd.DataFrame()
    
    def _get_period_param(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> str:
        """Determina il parametro periodo per ANSA"""
        if not start_date or not end_date:
            return ""
        
        delta_days = (end_date - start_date).days
        
        if delta_days <= 7:
            return "7"
        elif delta_days <= 31:
            return "31"
        elif delta_days <= 365:
            return "365"
        else:
            return ""
