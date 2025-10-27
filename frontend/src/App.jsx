import React, { useMemo, useState, useEffect } from "react";
import { Globe2, BellRing, FileText, Sparkles, ShieldCheck, Lock, Download, ChevronRight, LineChart, Search, RefreshCw } from "lucide-react";
import { getTopics, getStats, transformTopic } from "./services/api";

// Reference data
const COUNTRIES = [
  { code: "ALL", name: "Tutti" },
  { code: "ITA", name: "Italia" },
  { code: "GBR", name: "Regno Unito" },
  { code: "DEU", name: "Germania" },
  { code: "FRA", name: "Francia" },
  { code: "USA", name: "USA" },
  { code: "GLOBAL", name: "Globale" },
];

const SECTORS = ["Tutti", "News", "Tech", "Sport", "Finanza", "Intrattenimento"];

function Badge({ children, className = "" }) {
  return <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-neutral-100 text-neutral-700 ${className}`}>{children}</span>;
}

function Section({ title, action, children }) {
  return (
    <section className="mb-6">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-semibold">{title}</h2>
        {action}
      </div>
      <div className="bg-white/60 rounded-2xl p-3 shadow-sm border border-neutral-200">{children}</div>
    </section>
  );
}

function TrendCard({ topic, onOpen }) {
  return (
    <button onClick={() => onOpen(topic)} className="w-full text-left">
      <div className="rounded-2xl p-4 border border-neutral-200 bg-white hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge className="bg-indigo-50 text-indigo-700">{topic.country}</Badge>
              <Badge>{topic.sector}</Badge>
              <Badge className="bg-emerald-50 text-emerald-700">Pulse {topic.pulse}</Badge>
            </div>
            <h3 className="font-semibold text-neutral-900">{topic.title}</h3>
            <p className="text-sm text-neutral-600 mt-1 line-clamp-2">{topic.summary}</p>
            <div className="mt-2 flex items-center gap-3 text-xs text-neutral-500">
              <span className="inline-flex items-center gap-1"><LineChart className="w-4 h-4" /> vel {Math.round(topic.velocity * 100)}%</span>
              <span>spread {topic.spread}</span>
              <span>vol {topic.volume || 0}</span>
              <span>nov {Math.round(topic.novelty * 100)}%</span>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-neutral-400" />
        </div>
        <div className="mt-3 flex flex-wrap gap-1">
          {topic.sources.map((s) => <Badge key={s}>{s}</Badge>)}
        </div>
      </div>
    </button>
  );
}

function TopicDrawer({ open, topic, onClose, mode }) {
  if (!open || !topic) return null;
  const gated = mode === "consumer";
  return (
    <div className="fixed inset-0 bg-black/30 flex justify-end z-50">
      <div className="w-full max-w-xl h-full bg-white p-5 overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-semibold">{topic.title}</h3>
          <button onClick={onClose} className="text-neutral-500 hover:text-neutral-800">Chiudi</button>
        </div>
        <p className="mt-2 text-neutral-600">{topic.summary}</p>
        <div className="mt-4 grid grid-cols-3 gap-3">
          <div className="rounded-xl border p-3">
            <div className="text-sm text-neutral-500">Pulse Score</div>
            <div className="text-2xl font-semibold">{topic.pulse}</div>
          </div>
          <div className="rounded-xl border p-3">
            <div className="text-sm text-neutral-500">Volume 24h</div>
            <div className="text-2xl font-semibold">{topic.volume || 0}</div>
          </div>
          <div className="rounded-xl border p-3">
            <div className="text-sm text-neutral-500">Velocity</div>
            <div className="text-2xl font-semibold">{Math.round((topic.velocity || 0) * 100)}%</div>
          </div>
          <div className="rounded-xl border p-3">
            <div className="text-sm text-neutral-500">Spread</div>
            <div className="text-2xl font-semibold">{topic.spread}</div>
          </div>
          <div className="rounded-xl border p-3">
            <div className="text-sm text-neutral-500">Authority</div>
            <div className="text-2xl font-semibold">{Math.round((topic.authority || 0) * 100)}%</div>
          </div>
          <div className="rounded-xl border p-3">
            <div className="text-sm text-neutral-500">Novelty</div>
            <div className="text-2xl font-semibold">{Math.round((topic.novelty || 0) * 100)}%</div>
          </div>
        </div>
        <Section title="Timeline 72h" action={<Badge>demo</Badge>}>
          <div className="h-32 bg-gradient-to-br from-indigo-50 to-white rounded-xl border flex items-center justify-center text-neutral-400">Sparkline</div>
        </Section>
        <Section title="Fonti principali" action={<Badge>citazioni</Badge>}>
          <ul className="list-disc ml-5 text-sm text-neutral-700">
            {topic.sources.map((s) => (
              <li key={s}><span className="font-medium">{s}</span> — snippet … <a className="text-indigo-600" href="#">link</a></li>
            ))}
          </ul>
        </Section>
        <Section title="Forecast 48h" action={<Badge>beta</Badge>}>
          <div className="h-28 rounded-xl border flex items-center justify-center">
            {gated ? (
              <div className="flex items-center gap-2 text-neutral-500"><Lock className="w-4 h-4" />Disponibile nei piani Team/Business</div>
            ) : (
              <div className="text-neutral-600">Intervallo di confidenza e proiezione (placeholder)</div>
            )}
          </div>
        </Section>
        <div className="mt-4 flex gap-2">
          <button className="px-3 py-2 rounded-xl bg-neutral-900 text-white flex items-center gap-2"><BellRing className="w-4 h-4" /> Crea alert</button>
          <button className="px-3 py-2 rounded-xl border flex items-center gap-2"><Download className="w-4 h-4" /> Esporta</button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [mode, setMode] = useState("business");
  const [country, setCountry] = useState("ALL");
  const [sector, setSector] = useState("Tutti");
  const [query, setQuery] = useState("");
  const [openTopic, setOpenTopic] = useState(null);
  
  // Backend data - Phase 2: real topics from ML clustering
  const [rawTopics, setRawTopics] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const gated = mode === "consumer";

  // Load data from backend
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    console.log('🔄 Loading topics from API...');
    try {
      const [topicsData, statsData] = await Promise.all([
        getTopics({ limit: 50, sort_by: 'pulse_score' }),
        getStats(),
      ]);
      console.log('✅ Received topics:', topicsData);
      console.log('✅ Received stats:', statsData);
      // Transform topics to UI format
      const transformed = topicsData.map(transformTopic);
      console.log('✅ Transformed topics:', transformed);
      setRawTopics(transformed);
      setStats(statsData);
    } catch (err) {
      console.error('❌ Failed to load data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Filter topics (no grouping needed - ML already clustered them!)
  const topics = useMemo(() => {
    let filtered = [...rawTopics];
    if (country !== "ALL") filtered = filtered.filter(t => t.country === country);
    if (sector !== "Tutti") filtered = filtered.filter(t => t.sector === sector);
    if (query) filtered = filtered.filter(t => 
      t.title.toLowerCase().includes(query.toLowerCase()) ||
      t.summary.toLowerCase().includes(query.toLowerCase())
    );
    return filtered.sort((a, b) => b.pulse - a.pulse);
  }, [rawTopics, country, sector, query]);

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Top bar */}
      <header className="sticky top-0 z-40 backdrop-blur bg-white/80 border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <span className="font-semibold">Pulse</span>
            <Badge className="ml-2">MVP</Badge>
            {stats && (
              <span className="hidden md:inline text-xs text-neutral-500 ml-2">
                {stats.total_articles} articoli • {stats.last_24h} ultime 24h
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={loadData} 
              disabled={loading}
              className="px-2 py-1.5 rounded-xl border hover:bg-neutral-50 disabled:opacity-50"
              title="Ricarica dati"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <div className="hidden md:flex items-center gap-2">
              <button className={`px-3 py-1.5 rounded-xl border ${mode === 'consumer' ? 'bg-neutral-900 text-white' : 'bg-white'}`} onClick={() => setMode("consumer")}>Utente</button>
              <button className={`px-3 py-1.5 rounded-xl border ${mode === 'business' ? 'bg-neutral-900 text-white' : 'bg-white'}`} onClick={() => setMode("business")}>Azienda</button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-6">
          <div className="col-span-2 flex items-center gap-2 rounded-2xl border bg-white px-3 py-2">
            <Search className="w-4 h-4 text-neutral-400" />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Cerca argomento, persona, brand…" className="w-full outline-none" />
          </div>
          <select value={country} onChange={(e) => setCountry(e.target.value)} className="rounded-2xl border bg-white px-3 py-2">
            {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
          </select>
          <select value={sector} onChange={(e) => setSector(e.target.value)} className="rounded-2xl border bg-white px-3 py-2">
            {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        {/* World / Country map */}
        <Section title="Mappa del battito" action={<Badge><Globe2 className="w-4 h-4 mr-1 inline" /> {country}</Badge>}>
          <div className="h-56 rounded-2xl border bg-gradient-to-br from-neutral-100 to-white flex items-center justify-center text-neutral-400">
            {gated ? (
              <div className="flex items-center gap-2"><Lock className="w-4 h-4" /> Live tra 24h (freemium)</div>
            ) : (
              <div>Placeholder mappa (choropleth / heat)</div>
            )}
          </div>
        </Section>

        {/* Top trends */}
        <Section title="Top trends" action={<Badge>{gated ? "ritardo 24h" : `${topics.length} topics • live`}</Badge>}>
          {loading ? (
            <div className="flex items-center justify-center h-40 text-neutral-400">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-40 text-red-500">
              Errore: {error}
            </div>
          ) : topics.length === 0 ? (
            <div className="flex items-center justify-center h-40 text-neutral-400">
              Nessun topic trovato con i filtri selezionati
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {topics.map(t => <TrendCard key={t.id} topic={t} onOpen={setOpenTopic} />)}
            </div>
          )}
        </Section>

        {/* Business-only sections */}
        {mode === "business" && (
          <div className="grid md:grid-cols-3 gap-4">
            <Section title="Alert Center" action={<Badge><BellRing className="w-4 h-4 mr-1 inline" /> illimitati</Badge>}>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between border rounded-xl p-2">
                  <div>
                    <div className="font-medium">Crisi brand (IT, sentiment var &gt; 0.8)</div>
                    <div className="text-neutral-500">Slack #pulse-alerts • 24/7 • dedup 15m</div>
                  </div>
                  <button className="px-2 py-1 rounded-lg border">Modifica</button>
                </div>
                <button className="px-3 py-2 rounded-xl bg-neutral-900 text-white">Nuovo alert</button>
              </div>
            </Section>
            <Section title="Report Builder" action={<Badge><FileText className="w-4 h-4 mr-1 inline" /> PDF</Badge>}>
              <div className="space-y-2 text-sm">
                <div className="grid grid-cols-2 gap-2">
                  <select className="rounded-xl border px-2 py-1"><option>Ultime 2 settimane</option><option>Ultimo mese</option></select>
                  <select className="rounded-xl border px-2 py-1"><option>Italia</option><option>EU5</option><option>Custom</option></select>
                </div>
                <button className="px-3 py-2 rounded-xl border flex items-center gap-2"><Download className="w-4 h-4" /> Genera report</button>
              </div>
            </Section>
            <Section title="Amministrazione" action={<Badge><ShieldCheck className="w-4 h-4 mr-1 inline" /> SSO</Badge>}>
              <ul className="text-sm text-neutral-700 space-y-1">
                <li>Utenti & Ruoli (viewer, analyst, admin)</li>
                <li>Chiavi API e quota</li>
                <li>Data retention & compliance</li>
              </ul>
            </Section>
          </div>
        )}
      </main>

      <footer className="py-6 text-center text-xs text-neutral-500">Pulse MVP • Realtime Trend Intelligence</footer>

      <TopicDrawer open={!!openTopic} topic={openTopic} onClose={() => setOpenTopic(null)} mode={mode} />
    </div>
  );
}
