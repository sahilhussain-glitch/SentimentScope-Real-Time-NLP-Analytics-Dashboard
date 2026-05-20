import { useState, useEffect } from "react";
import axios from "axios";

const API = "http://localhost:8002";

const SENTIMENT_COLORS = {
  positive: "#22c55e", negative: "#ef4444", neutral: "#94a3b8",
  mixed: "#f59e0b", frustrated: "#dc2626", excited: "#8b5cf6",
  confused: "#f97316", satisfied: "#10b981", disappointed: "#6b7280", urgent: "#ef4444"
};

export default function App() {
  const [text, setText] = useState("");
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("analyze");

  async function loadStats() {
    const res = await axios.get(`${API}/api/stats`);
    setStats(res.data);
  }

  async function loadResults() {
    const res = await axios.get(`${API}/api/results`);
    setResults(res.data.results);
  }

  useEffect(() => { loadStats(); loadResults(); }, []);

  async function handleAnalyze() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/analyze/text`, { text });
      setResults(prev => [res.data, ...prev]);
      await loadStats();
      setText("");
    } catch (e) {
      alert("Error: " + (e.response?.data?.detail || e.message));
    }
    setLoading(false);
  }

  async function handleCSV(e) {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await axios.post(`${API}/api/analyze/csv`, form);
      setResults(prev => [...res.data, ...prev]);
      await loadStats();
    } catch (e) {
      alert("CSV Error: " + (e.response?.data?.detail || e.message));
    }
    setLoading(false);
  }

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <header style={{ borderBottom: "3px solid #1A56DB", paddingBottom: "1rem", marginBottom: "2rem" }}>
        <h1 style={{ color: "#1A56DB", margin: 0 }}>📊 SentimentScope</h1>
        <p style={{ color: "#5A5A72", margin: "0.3rem 0 0" }}>Real-Time NLP Analytics Dashboard</p>
      </header>

      {/* Stats bar */}
      {stats && (
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem", flexWrap: "wrap" }}>
          {[
            { label: "Total Analyzed", value: stats.total },
            { label: "Avg Score", value: stats.avg_score?.toFixed(2) },
            ...Object.entries(stats.sentiment_counts || {}).slice(0, 4).map(([k, v]) => ({ label: k, value: v }))
          ].map(({ label, value }) => (
            <div key={label} style={{ background: "#f0f4ff", borderRadius: 8, padding: "0.75rem 1.25rem", minWidth: 100 }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: "#1A56DB" }}>{value}</div>
              <div style={{ fontSize: 12, color: "#5A5A72" }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
        {["analyze", "results"].map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "0.5rem 1.25rem", border: "none", borderRadius: 6, cursor: "pointer",
              background: tab === t ? "#1A56DB" : "#f0f4ff", color: tab === t ? "#fff" : "#1A56DB", fontWeight: 600 }}>
            {t === "analyze" ? "Analyze Text" : `Results (${results.length})`}
          </button>
        ))}
      </div>

      {tab === "analyze" && (
        <div>
          <textarea value={text} onChange={e => setText(e.target.value)}
            placeholder="Paste a review, tweet, or feedback here..."
            style={{ width: "100%", height: 120, padding: "0.75rem", borderRadius: 8,
              border: "1px solid #cbd5e1", fontSize: 15, resize: "vertical", boxSizing: "border-box" }} />
          <div style={{ display: "flex", gap: "1rem", marginTop: "0.75rem", alignItems: "center" }}>
            <button onClick={handleAnalyze} disabled={loading}
              style={{ padding: "0.75rem 2rem", background: "#1A56DB", color: "#fff",
                border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 700 }}>
              {loading ? "Analyzing..." : "Analyze"}
            </button>
            <label style={{ padding: "0.75rem 1.5rem", background: "#f0f4ff", color: "#1A56DB",
              borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>
              Upload CSV
              <input type="file" accept=".csv" onChange={handleCSV} style={{ display: "none" }} />
            </label>
          </div>
        </div>
      )}

      {tab === "results" && (
        <div>
          {results.length === 0
            ? <p style={{ color: "#9ca3af" }}>No results yet. Analyze some text first.</p>
            : results.map(r => (
              <div key={r.id} style={{ background: "#f8faff", border: "1px solid #e5e7eb",
                borderRadius: 10, padding: "1rem 1.25rem", marginBottom: "0.75rem",
                borderLeft: `4px solid ${SENTIMENT_COLORS[r.sentiment] || "#94a3b8"}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ background: SENTIMENT_COLORS[r.sentiment] || "#94a3b8",
                    color: "#fff", borderRadius: 20, padding: "0.2rem 0.75rem", fontSize: 13, fontWeight: 600 }}>
                    {r.sentiment}
                  </span>
                  <span style={{ color: "#5A5A72", fontSize: 13 }}>score: {r.score?.toFixed(2)}</span>
                </div>
                <p style={{ margin: "0.5rem 0", color: "#1E1E2E", fontSize: 14 }}>{r.text}</p>
                <p style={{ margin: 0, color: "#5A5A72", fontSize: 13 }}>{r.summary}</p>
                <div style={{ marginTop: "0.5rem", fontSize: 12, color: "#1A56DB" }}>
                  Topics: {r.topics?.join(", ")} &nbsp;·&nbsp; Keywords: {r.keywords?.join(", ")}
                </div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}
