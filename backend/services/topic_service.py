"""
Topic Service - Clustering articles without BERTopic dependency
Uses sentence-transformers + K-Means for ARM64 compatibility
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from models.article import Article
from models.topic import Topic
from models.database import get_db


class TopicService:
    """Service for topic clustering and management"""
    
    def __init__(self):
        # Initialize embedding model (multilingual)
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        self.tfidf_vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
        self.cluster_model = None
        
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for texts using sentence-transformers
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings
        """
        return self.embedding_model.encode(texts, show_progress_bar=True)
    
    def cluster_articles(
        self,
        articles: List[Article],
        min_cluster_size: int = 3
    ) -> Dict:
        """
        Cluster articles into topics using K-Means
        
        Args:
            articles: List of Article objects to cluster
            min_cluster_size: Minimum articles per cluster
            
        Returns:
            Dictionary with cluster assignments and topic info
        """
        if not articles:
            return {"topics": [], "assignments": [], "keywords": {}}
        
        # Prepare texts (title + content preview)
        texts = [f"{art.title}. {art.content[:500] if art.content else ''}" 
                 for art in articles]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} articles...")
        embeddings = self.generate_embeddings(texts)
        
        # Determine number of clusters (rule of thumb: sqrt(n/2))
        n_clusters = max(2, min(10, int(np.sqrt(len(articles) / 2))))
        print(f"Creating {n_clusters} clusters...")
        
        # K-Means clustering
        self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = self.cluster_model.fit_predict(embeddings)
        
        # Extract keywords using TF-IDF
        keywords_per_topic = {}
        for topic_id in range(n_clusters):
            topic_texts = [texts[i] for i in range(len(texts)) if labels[i] == topic_id]
            if topic_texts:
                try:
                    tfidf_matrix = self.tfidf_vectorizer.fit_transform(topic_texts)
                    feature_names = self.tfidf_vectorizer.get_feature_names_out()
                    
                    # Get top words
                    scores = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
                    top_indices = scores.argsort()[-10:][::-1]
                    keywords_per_topic[topic_id] = [feature_names[i] for i in top_indices if scores[i] > 0]
                except:
                    keywords_per_topic[topic_id] = []
        
        # Count articles per cluster
        unique, counts = np.unique(labels, return_counts=True)
        topic_counts = dict(zip(unique, counts))
        
        return {
            "assignments": labels,
            "n_clusters": n_clusters,
            "topic_counts": topic_counts,
            "keywords": keywords_per_topic
        }
    
    def extract_topic_keywords(self, topic_id: int, keywords_dict: Dict) -> List[str]:
        """
        Extract top keywords for a topic
        
        Args:
            topic_id: Cluster ID
            keywords_dict: Dictionary of keywords per topic
            
        Returns:
            List of keyword strings
        """
        return keywords_dict.get(topic_id, [])[:10]
    
    def generate_topic_label(self, articles: List[Article], keywords: List[str]) -> str:
        """
        Generate a human-readable label for a topic
        
        Uses the most representative article title or combines keywords
        
        Args:
            articles: Articles in this topic
            keywords: Topic keywords from BERTopic
            
        Returns:
            Topic label string
        """
        if not articles:
            return " ".join(keywords[:3]) if keywords else "Unknown Topic"
        
        # Use the title of the first article (most representative)
        # Or combine top keywords
        if articles[0].title and len(articles[0].title) > 10:
            return articles[0].title[:100]
        else:
            return " ".join(keywords[:4])
    
    def cluster_and_save_topics(
        self,
        days_back: int = 7,
        min_cluster_size: int = 3
    ) -> List[Topic]:
        """
        Main method: cluster recent articles and save topics to database
        
        Args:
            days_back: Number of days to look back for articles
            min_cluster_size: Minimum articles per topic
            
        Returns:
            List of created Topic objects
        """
        db = next(get_db())
        
        # Get recent articles
        cutoff_date = datetime.now() - timedelta(days=days_back)
        articles = db.query(Article).filter(
            Article.scraped_at >= cutoff_date
        ).all()
        
        if not articles:
            print("No articles found for clustering")
            return []
        
        print(f"Clustering {len(articles)} articles from last {days_back} days...")
        
        # Cluster
        result = self.cluster_articles(articles, min_cluster_size=min_cluster_size)
        
        if not result or "assignments" not in result:
            print("Clustering failed")
            return []
        
        assignments = result["assignments"]
        keywords_dict = result["keywords"]
        topic_counts = result["topic_counts"]
        
        # Create Topic objects
        created_topics = []
        
        for topic_id in topic_counts.keys():
            # Get articles in this cluster
            cluster_articles = [art for art, label in zip(articles, assignments) 
                              if label == topic_id]
            
            if not cluster_articles:
                continue
            
            # Extract keywords
            keywords = self.extract_topic_keywords(topic_id, keywords_dict)
            
            # Generate label
            label = self.generate_topic_label(cluster_articles, keywords)
            
            # Determine primary country and sector
            countries = [art.country for art in cluster_articles if art.country]
            sectors = [art.sector for art in cluster_articles if art.sector]
            
            primary_country = max(set(countries), key=countries.count) if countries else 'GLOBAL'
            primary_sector = max(set(sectors), key=sectors.count) if sectors else 'News'
            
            # Create Topic
            topic = Topic(
                topic_id=f"topic_{topic_id}",
                label=label,
                keywords=keywords,
                description=f"Cluster of {len(cluster_articles)} articles",
                country=primary_country,
                sector=primary_sector,
                first_seen=min(art.published_at for art in cluster_articles 
                             if art.published_at),
                last_updated=datetime.now()
            )
            
            db.add(topic)
            created_topics.append(topic)
            
            # Link articles to topic
            for article in cluster_articles:
                article.topic_id = topic.topic_id
            
            print(f"Created topic: {topic.topic_id} - {label[:50]}... ({len(cluster_articles)} articles)")
        
        # Commit all changes
        db.commit()
        
        print(f"✅ Created {len(created_topics)} topics")
        
        return created_topics
    
    def recalculate_topics(self, min_cluster_size: int = 3) -> List[Topic]:
        """
        Recalculate all topics from scratch (for periodic updates)
        
        Args:
            min_cluster_size: Minimum articles per topic
            
        Returns:
            List of updated Topic objects
        """
        db = next(get_db())
        
        # Clear existing topic assignments
        db.query(Article).update({"topic_id": None})
        db.query(Topic).delete()
        db.commit()
        
        # Recluster
        return self.cluster_and_save_topics(days_back=7, min_cluster_size=min_cluster_size)


# Singleton instance
topic_service = TopicService()
