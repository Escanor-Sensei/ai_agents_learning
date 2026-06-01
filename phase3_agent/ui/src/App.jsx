import { useState } from 'react'

const API = 'http://localhost:8000'

const STAGES = [
  { key: 'research_notes', label: '🔍 Research Notes' },
  { key: 'outline',        label: '📋 Outline' },
  { key: 'blog_post',      label: '✍️ Blog Post' },
]

const NODE_LABELS = {
  researcher: '🔍 Research Notes',
  analyst:    '📋 Outline',
  writer:     '✍️ Blog Post',
}

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
  const [topic, setTopic]       = useState('')
  const [result, setResult]     = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [statusLabel, setStatusLabel] = useState('')
  const [streaming, setStreaming]     = useState({ researcher: '', analyst: '', writer: '' })
  const [activeNode, setActiveNode]   = useState(null)

  async function handleGenerate(e) {
    e.preventDefault()
    if (topic.trim().length < 3) return

    setLoading(true)
    setError('')
    setResult(null)
    setStatusLabel('')
    setStreaming({ researcher: '', analyst: '', writer: '' })
    setActiveNode(null)

    try {
      const res = await fetch(`${API}/generate/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Request failed')
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(l => l.startsWith('data: '))

        for (const line of lines) {
          const raw = line.slice(6).trim()
          if (raw === '[DONE]') break

          const event = JSON.parse(raw)

          if (event.type === 'label') {
            setStatusLabel(event.text)
            setActiveNode(event.node)
          }

          else if (event.type === 'token') {
            setStreaming(prev => ({
              ...prev,
              [event.node]: (prev[event.node] || '') + event.token,
            }))
          }

          else if (event.type === 'result') {
            setResult(event)
            setStatusLabel('')
            setActiveNode(null)
          }

          else if (event.type === 'error') {
            throw new Error(event.message)
          }
        }
      }
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

      {/* Live streaming view */}
      {loading && (
        <div className="pipeline-status">
          {statusLabel && <p className="status-label">{statusLabel}</p>}

          {Object.entries(NODE_LABELS).map(([node, label]) => {
            const text = streaming[node]
            if (!text && activeNode !== node) return null
            return (
              <div key={node} className={`section ${activeNode === node ? 'highlight' : ''}`}>
                <div className="section-header"><span>{label}</span></div>
                <pre className="section-body">{text}{activeNode === node && <span className="cursor">▌</span>}</pre>
              </div>
            )
          })}
        </div>
      )}

      {/* Final result */}
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
            <Section label="🧑⚖️ Supervisor Feedback" content={result.supervisor_feedback} highlight={false} />
          )}
        </div>
      )}
    </div>
  )
}
