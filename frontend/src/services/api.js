/**
 * API Service - Backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API call failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Get articles with filters
 */
export async function getArticles({
  limit = 50,
  offset = 0,
  source = null,
  language = null,
  country = null,
  search = null,
} = {}) {
  const params = new URLSearchParams();
  params.append('limit', limit);
  params.append('offset', offset);
  if (source) params.append('source', source);
  if (language) params.append('language', language);
  if (country) params.append('country', country);
  if (search) params.append('search', search);

  return fetchAPI(`/api/articles/?${params.toString()}`);
}

/**
 * Get single article by ID
 */
export async function getArticle(id) {
  return fetchAPI(`/api/articles/${id}`);
}

/**
 * Get statistics overview
 */
export async function getStats() {
  return fetchAPI('/api/stats/overview');
}

/**
 * Get statistics by source
 */
export async function getSourceStats() {
  return fetchAPI('/api/stats/sources');
}

/**
 * Get statistics by language
 */
export async function getLanguageStats() {
  return fetchAPI('/api/stats/languages');
}

/**
 * Get statistics by country
 */
export async function getCountryStats() {
  return fetchAPI('/api/stats/countries');
}

/**
 * Get available scraping sources
 */
export async function getSources() {
  return fetchAPI('/api/scraping/sources');
}

/**
 * Trigger scraping job (async)
 */
export async function scrapeArticles({
  query,
  sources = null,
  max_pages = 3,
  days_back = 7,
}) {
  return fetchAPI('/api/scraping/scrape', {
    method: 'POST',
    body: JSON.stringify({
      query,
      sources,
      max_pages,
      days_back,
    }),
  });
}

/**
 * Trigger scraping and wait for results (sync)
 */
export async function scrapeArticlesNow({
  query,
  sources = null,
  max_pages = 3,
  days_back = 7,
}) {
  return fetchAPI('/api/scraping/scrape-now', {
    method: 'POST',
    body: JSON.stringify({
      query,
      sources,
      max_pages,
      days_back,
    }),
  });
}

/**
 * Transform article to topic format for UI
 */
export function articleToTopic(article) {
  return {
    id: article.id,
    title: article.title,
    summary: article.content?.substring(0, 150) + '...' || '',
    country: article.country || 'GLOBAL',
    sector: article.sector || 'News',
    pulse: Math.round(article.engagement_score * 100) || 50,
    velocity: article.engagement_score || 0.5,
    spread: 1,
    sentiment: article.sentiment_score || 0,
    sources: [article.source],
    published_at: article.published_at,
    url: article.url,
    language: article.language,
  };
}

/**
 * Group articles by similar titles (basic topic clustering)
 */
export function groupArticlesByTopic(articles) {
  const topics = new Map();
  
  articles.forEach(article => {
    // Simple keyword extraction from title
    const keywords = article.title
      .toLowerCase()
      .split(/\s+/)
      .filter(w => w.length > 4)
      .slice(0, 3)
      .sort()
      .join(' ');
    
    if (!topics.has(keywords)) {
      topics.set(keywords, {
        id: `topic-${topics.size}`,
        title: article.title,
        summary: article.content?.substring(0, 150) + '...' || '',
        country: article.country || 'GLOBAL',
        sector: article.sector || 'News',
        pulse: 50,
        velocity: 0.5,
        spread: 1,
        sentiment: article.sentiment_score || 0,
        sources: [article.source],
        articles: [article],
        published_at: article.published_at,
      });
    } else {
      const topic = topics.get(keywords);
      topic.sources.push(article.source);
      topic.articles.push(article);
      topic.spread = topic.articles.length;
      // Update pulse based on article count
      topic.pulse = Math.min(100, 50 + (topic.articles.length * 10));
      topic.velocity = Math.min(1, 0.5 + (topic.articles.length * 0.1));
    }
  });
  
  return Array.from(topics.values())
    .sort((a, b) => b.pulse - a.pulse);
}
