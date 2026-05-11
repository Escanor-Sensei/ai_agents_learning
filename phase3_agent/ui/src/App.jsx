import { useState } from 'react'

const API = 'http://localhost:8000'

const STAGES = [
  { key: 'research_notes', label: '🔍 Research Notes' },
  { key: 'outline',        label: '📋 Outline' },
  { key: 'blog_post',      label: '✍️ Blog Post' },
]

function Section({ label, content, highlight }) {
  const [open, setOpen] = useState(highlight)
  return (
    <div className={`section ${highlight ? 'highlight' : ''}`}>
      <button className="section-header" onClick={() => setOpen(o => !o)}>
        <span>{label}</span>
        <span className="chevron">{open ? '▲' : '▼'}</span>
      </button>
      {open && <pre className="section-body">{content}</pre>}
    </div>
  )
}

export default function App() {
  const [topic, setTopic]   = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState('')

  async function handleGenerate(e) {
    e.preventDefault()
    if (topic.trim().length < 3) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${API}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Request failed')
      }
      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>✦ Blog Generator</h1>
        <p className="subtitle">Multi-agent pipeline: Researcher → Analyst → Writer → Supervisor</p>
      </header>

      <form className="form" onSubmit={handleGenerate}>
        <input
          className="topic-input"
          placeholder="Enter a blog topic…"
          value={topic}
          onChange={e => setTopic(e.target.value)}
          disabled={loading}
        />
        <button className="generate-btn" type="submit" disabled={loading || topic.trim().length < 3}>
          {loading ? <span className="spinner" /> : 'Generate'}
        </button>
      </form>

      {error && <div className="error">⚠ {error}</div>}

      {loading && (
        <div className="pipeline-status">
          <div className="pulse-row">
            {['Researching', 'Outlining', 'Writing', 'Reviewing'].map(s => (
              <span key={s} className="pulse-chip">{s}</span>
            ))}
          </div>
          <p className="loading-hint">Running pipeline… this may take a minute.</p>
        </div>
      )}

      {result && (
        <div className="result">
          <div className="meta-bar">
            <span>Topic: <strong>{result.topic}</strong></span>
            <span>{result.retry_count === 0 ? '✅ Passed first try' : `🔁 Retries: ${result.retry_count}`}</span>
            {result.supervisor_feedback && (
              <span className="feedback-badge" title={result.supervisor_feedback}>
                💬 Supervisor feedback
              </span>
            )}
          </div>

          {STAGES.map(({ key, label }) => (
            <Section key={key} label={label} content={result[key]} highlight={key === 'blog_post'} />
          ))}

          {result.supervisor_feedback && (
            <Section label="🧑‍⚖️ Supervisor Feedback" content={result.supervisor_feedback} highlight={false} />
          )}
        </div>
      )}
    </div>
  )
}
