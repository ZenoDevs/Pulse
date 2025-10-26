"""
Language Detection Service
Detecta lingua e georeferenziazione degli articoli
"""
from typing import Optional, Dict
from langdetect import detect, LangDetectException
import re


class LanguageService:
    """Servizio per detection lingua e geo-tagging"""
    
    # Mapping country codes
    COUNTRY_CODES = {
        'it': 'ITA', 'en': 'USA', 'de': 'DEU', 
        'fr': 'FRA', 'es': 'ESP', 'pt': 'PRT',
        'nl': 'NLD', 'pl': 'POL', 'ru': 'RUS',
        'zh-cn': 'CHN', 'ja': 'JPN', 'ko': 'KOR'
    }
    
    # Keywords geo per override
    GEO_KEYWORDS = {
        'ITA': ['italia', 'rome', 'roma', 'milano', 'italian'],
        'USA': ['usa', 'america', 'washington', 'new york', 'american'],
        'GBR': ['uk', 'britain', 'london', 'british', 'england'],
        'DEU': ['germany', 'berlin', 'german', 'deutschland'],
        'FRA': ['france', 'paris', 'french', 'française'],
        'CHN': ['china', 'beijing', 'chinese', 'shanghai'],
    }
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detecta la lingua del testo
        Returns: ISO 639-1 code (it, en, de, etc.)
        """
        if not text or len(text.strip()) < 10:
            return None
        
        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return None
    
    def detect_country(
        self, 
        text: str, 
        title: str = "", 
        language: Optional[str] = None
    ) -> Optional[str]:
        """
        Determina il paese di riferimento
        Returns: ISO 3166-1 alpha-3 code (ITA, USA, etc.)
        """
        # Step 1: Check keywords geografiche nel titolo/testo
        combined_text = f"{title} {text}".lower()
        
        for country_code, keywords in self.GEO_KEYWORDS.items():
            if any(kw in combined_text for kw in keywords):
                return country_code
        
        # Step 2: Fallback su lingua
        if language:
            return self.COUNTRY_CODES.get(language, 'GLOBAL')
        
        return 'GLOBAL'
    
    def extract_entities(self, text: str) -> Dict[str, list]:
        """
        Estrae entità base (luoghi, organizzazioni)
        Simple regex-based extraction
        """
        entities = {
            'locations': [],
            'organizations': []
        }
        
        # Estrai capitalized words (potenziali entità)
        # Pattern: sequenze di 2+ parole capitalize
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        matches = re.findall(pattern, text)
        
        # Filtro base: locations se contengono keyword comuni
        location_keywords = ['city', 'country', 'province', 'region', 'state']
        
        for match in matches:
            if any(kw in match.lower() for kw in location_keywords):
                entities['locations'].append(match)
            else:
                entities['organizations'].append(match)
        
        # Deduplica
        entities['locations'] = list(set(entities['locations']))
        entities['organizations'] = list(set(entities['organizations']))
        
        return entities
    
    def enrich_article(self, article_data: dict) -> dict:
        """
        Arricchisce l'articolo con language, country, entities
        """
        text = article_data.get('content', '')
        title = article_data.get('title', '')
        
        # Detect language
        language = self.detect_language(text)
        
        # Detect country
        country = self.detect_country(text, title, language)
        
        # Extract entities
        entities = self.extract_entities(f"{title}. {text}")
        
        # Aggiungi al dict
        article_data['language'] = language
        article_data['country'] = country
        article_data['entities'] = entities
        
        return article_data


# Singleton instance
language_service = LanguageService()
