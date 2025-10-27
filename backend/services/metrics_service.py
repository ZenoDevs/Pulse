"""
Metrics Service
Calcola i 6 Pulse Metrics per ogni topic
"""
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.topic import Topic
from models.article import Article
from models.database import SessionLocal


# Authority scores per fonte (0.0 - 1.0)
AUTHORITY_SCORES = {
    'ansa': 0.9,
    'reuters': 0.95,
    'bbc': 0.9,
    'reddit': 0.4,
    'hackernews': 0.6,
    'twitter': 0.3,
    'default': 0.5
}


class MetricsService:
    """Servizio per calcolare Pulse Metrics"""
    
    def __init__(self):
        pass
    
    def calculate_volume(self, articles: List[Article]) -> int:
        """
        Volume: numero di articoli nel topic nelle ultime 24h
        
        Returns:
            int: count articoli ultimi 24h
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=24)
        
        recent_articles = [
            art for art in articles 
            if art.published_at and art.published_at >= cutoff
        ]
        
        return len(recent_articles)
    
    def calculate_velocity(
        self, 
        articles: List[Article],
        topic: Topic
    ) -> float:
        """
        Velocity: crescita percentuale volume nelle ultime 24h
        
        Formula: (volume_now - volume_24h_ago) / volume_24h_ago
        
        Returns:
            float: velocity (-1.0 a +∞)
                   +0.5 = +50% crescita
                   -0.5 = -50% calo
        """
        now = datetime.utcnow()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_48h = now - timedelta(hours=48)
        
        # Volume ultime 24h
        volume_now = len([
            art for art in articles
            if art.published_at and art.published_at >= cutoff_24h
        ])
        
        # Volume 24-48h fa
        volume_previous = len([
            art for art in articles
            if art.published_at 
            and cutoff_48h <= art.published_at < cutoff_24h
        ])
        
        if volume_previous == 0:
            # Topic nuovo o nessun articolo nel periodo precedente
            return 1.0 if volume_now > 0 else 0.0
        
        velocity = (volume_now - volume_previous) / volume_previous
        return round(velocity, 2)
    
    def calculate_spread(self, articles: List[Article]) -> int:
        """
        Spread: numero di fonti distinte che parlano del topic
        
        Returns:
            int: count fonti uniche (1 a N)
        """
        sources = set(art.source for art in articles if art.source)
        return len(sources)
    
    def calculate_authority(self, articles: List[Article]) -> float:
        """
        Authority: credibilità media delle fonti (0.0 - 1.0)
        
        Pesata sui punteggi di autorità delle fonti
        
        Returns:
            float: score medio 0.0-1.0
        """
        if not articles:
            return 0.0
        
        total_authority = sum(
            AUTHORITY_SCORES.get(art.source, AUTHORITY_SCORES['default'])
            for art in articles
        )
        
        authority = total_authority / len(articles)
        return round(authority, 2)
    
    def calculate_novelty(self, topic: Topic) -> float:
        """
        Novelty: quanto è "fresco" il topic (0.0 - 1.0)
        
        Formula: 1.0 / (1.0 + hours_since_first_seen / 24.0)
        
        Topic nuovi hanno novelty ~1.0
        Topic vecchi decadono verso 0.0
        
        Returns:
            float: score 0.0-1.0
        """
        if not topic.first_seen:
            return 1.0
        
        now = datetime.utcnow()
        hours_since_first = (now - topic.first_seen).total_seconds() / 3600
        
        novelty = 1.0 / (1.0 + hours_since_first / 24.0)
        return round(novelty, 2)
    
    def calculate_pulse_score(
        self,
        volume: int,
        velocity: float,
        spread: int,
        authority: float,
        novelty: float
    ) -> float:
        """
        PulseScore: metrica composita pesata
        
        Formula:
            pulse_score = (
                volume * 0.25 +
                (velocity + 1.0) * 0.3 +     # Normalizza velocity a [0, ∞)
                spread * 0.15 +
                authority * 100 * 0.15 +
                novelty * 100 * 0.15
            )
        
        Pesi:
        - Volume: 25% (articoli grezzi)
        - Velocity: 30% (crescita)
        - Spread: 15% (diffusione)
        - Authority: 15% (credibilità)
        - Novelty: 15% (freschezza)
        
        Returns:
            float: PulseScore (0 a ~200+)
        """
        pulse = (
            volume * 0.25 +
            (velocity + 1.0) * 0.3 +
            spread * 0.15 +
            authority * 100 * 0.15 +
            novelty * 100 * 0.15
        )
        
        return round(pulse, 2)
    
    def calculate_all_metrics(
        self,
        topic: Topic,
        articles: List[Article],
        db: Session = None
    ) -> Dict[str, float]:
        """
        Calcola tutti i 6 metrics per un topic
        
        Args:
            topic: Topic object
            articles: Lista articoli appartenenti al topic
            db: Database session (opzionale, per update)
        
        Returns:
            dict: {
                'volume': int,
                'velocity': float,
                'spread': int,
                'authority': float,
                'novelty': float,
                'pulse_score': float
            }
        """
        # Calcola singoli metrics
        volume = self.calculate_volume(articles)
        velocity = self.calculate_velocity(articles, topic)
        spread = self.calculate_spread(articles)
        authority = self.calculate_authority(articles)
        novelty = self.calculate_novelty(topic)
        
        # Calcola PulseScore composito
        pulse_score = self.calculate_pulse_score(
            volume, velocity, spread, authority, novelty
        )
        
        metrics = {
            'volume': volume,
            'velocity': velocity,
            'spread': spread,
            'authority': authority,
            'novelty': novelty,
            'pulse_score': pulse_score
        }
        
        # Update topic nel DB se session fornita
        if db:
            topic.volume = volume
            topic.velocity = velocity
            topic.spread = spread
            topic.authority = authority
            topic.novelty = novelty
            topic.pulse_score = pulse_score
            topic.last_updated = datetime.utcnow()
            db.commit()
        
        return metrics
    
    def update_all_topics_metrics(self, db: Session = None) -> int:
        """
        Ricalcola metrics per tutti i topic attivi
        
        Chiamare periodicamente (es. ogni 1h) per aggiornare metrics
        
        Args:
            db: Database session
        
        Returns:
            int: numero di topic aggiornati
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        
        try:
            # Query tutti i topic
            topics = db.query(Topic).all()
            
            updated_count = 0
            
            for topic in topics:
                # Query articoli del topic
                articles = db.query(Article).filter(
                    Article.topic_id == topic.topic_id
                ).all()
                
                if articles:
                    # Calcola e aggiorna metrics
                    self.calculate_all_metrics(topic, articles, db)
                    updated_count += 1
            
            print(f"✅ Updated metrics for {updated_count} topics")
            return updated_count
            
        finally:
            if should_close:
                db.close()


# Singleton instance
metrics_service = MetricsService()
