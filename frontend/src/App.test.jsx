import React, { useState, useEffect } from "react";
import { RefreshCw } from "lucide-react";
import { getArticles, getStats } from "./services/api";

export default function App() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const statsData = await getStats();
      setStats(statsData);
      console.log('Stats loaded:', statsData);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Pulse - Test Connection</h1>
        
        {loading && (
          <div className="flex items-center gap-2">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Loading...</span>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {stats && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-semibold mb-4">Statistics</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="border rounded p-4">
                <div className="text-sm text-gray-500">Total Articles</div>
                <div className="text-3xl font-bold">{stats.total_articles}</div>
              </div>
              <div className="border rounded p-4">
                <div className="text-sm text-gray-500">Last 24h</div>
                <div className="text-3xl font-bold">{stats.last_24h}</div>
              </div>
            </div>
            
            <div className="mt-4">
              <h3 className="font-semibold mb-2">By Source:</h3>
              <pre className="bg-gray-100 p-2 rounded text-sm">
                {JSON.stringify(stats.by_source, null, 2)}
              </pre>
            </div>
            
            <div className="mt-4">
              <h3 className="font-semibold mb-2">By Language:</h3>
              <pre className="bg-gray-100 p-2 rounded text-sm">
                {JSON.stringify(stats.by_language, null, 2)}
              </pre>
            </div>
          </div>
        )}
        
        <button 
          onClick={loadData}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Reload Data
        </button>
      </div>
    </div>
  );
}
