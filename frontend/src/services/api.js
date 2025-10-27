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
 * Get topics with Pulse metrics (Phase 2)
 */
export async function getTopics({
  limit = 20,
  sort_by = 'pulse_score',
  country = null,
  sector = null,
} = {}) {
  const params = new URLSearchParams();
  params.append('limit', limit);
  params.append('sort_by', sort_by);
  if (country) params.append('country', country);
  if (sector) params.append('sector', sector);

  return fetchAPI(`/api/topics?${params.toString()}`);
}

/**
 * Get single topic by ID
 */
export async function getTopic(topicId) {
  return fetchAPI(`/api/topics/${topicId}`);
}

/**
 * Get articles for a specific topic
 */
export async function getTopicArticles(topicId, limit = 50) {
  const params = new URLSearchParams();
  params.append('limit', limit);
  return fetchAPI(`/api/topics/${topicId}/articles?${params.toString()}`);
}

/**
 * Refresh metrics for a specific topic
 */
export async function refreshTopicMetrics(topicId) {
  return fetchAPI(`/api/topics/${topicId}/refresh`, {
    method: 'POST',
  });
}

/**
 * Refresh metrics for all topics
 */
export async function refreshAllMetrics() {
  return fetchAPI('/api/topics/refresh-all', {
    method: 'POST',
  });
}

/**
 * Transform backend topic to UI format
 */
export function transformTopic(topic) {
  return {
    id: topic.topic_id,
    title: topic.label,
    summary: topic.description || '',
    keywords: topic.keywords || [],
    country: topic.country || 'GLOBAL',
    sector: topic.sector || 'News',
    pulse: Math.round(topic.pulse_score),
    velocity: topic.velocity,
    spread: topic.spread,
    authority: topic.authority,
    novelty: topic.novelty,
    volume: topic.volume,
    sentiment: topic.sentiment_avg || 0,
    sources: topic.sources || [],
    article_count: topic.article_count || 0,
    first_seen: topic.first_seen,
    last_updated: topic.last_updated,
  };
}
