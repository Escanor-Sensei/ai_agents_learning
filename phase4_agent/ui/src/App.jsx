import { useState, useRef } from 'react'

const API = 'http://localhost:8000'

const ROUND_LABELS = {
  pro_opening:  '🎤 Opening — Pro',
  con_opening:  '🎤 Opening — Con',
  pro_rebuttal: '⚔️ Rebuttal — Pro',
  con_rebuttal: '⚔️ Rebuttal — Con',
  pro_closing:  '🏁 Closing — Pro',
  con_closing:  '🏁 Closing — Con',
}

function ArgumentCard({ round, side, text, active }) {
  const [open, setOpen] = useState(true)
  return (
    <div className={`card ${side.toLowerCase()} ${active ? 'active' : ''}`}>
      <button className="card-header" onClick={() => setOpen(o => !o)}>
        <span>{ROUND_LABELS[round] ?? round}</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {active && <span className="live-dot" />}
          <span className="chevron">{open ? '▲' : '▼'}</span>
        </span>
      </button>
      {open && (
        <pre className="card-body">
          {text}
          {active && <span className="cursor">▌</span>}
        </pre>
      )}
    </div>
  )
}

export default function App() {
  const [topic, setTopic]     = useState('')
  const [status, setStatus]   = useState('')
  const [cards, setCards]     = useState([])   // [{ round, side, text }]
  const [result, setResult]   = useState(null)
  const [running, setRunning] = useState(false)
  const [error, setError]     = useState('')
  const activeNodeRef = useRef(null)

  async function handleDebate(e) {
    e.preventDefault()
    if (topic.trim().length < 3) return

    setRunning(true)
    setError('')
    setCards([])
    setResult(null)
    setStatus('')
    activeNodeRef.current = null

    try {
      const res = await fetch(`${API}/debate/stream`, {
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
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (raw === '[DONE]') { setStatus(''); break }

          const event = JSON.parse(raw)

          if (event.type === 'label') {
            setStatus(event.text)
            activeNodeRef.current = event.node
            if (event.node !== 'moderator')
              setCards(prev => [...prev, { round: event.node, side: event.node.startsWith('pro') ? 'Pro' : 'Con', text: '' }])
          }

          if (event.type === 'token') {
            // Append token to the last card
            setCards(prev => {
              const updated = [...prev]
              if (updated.length > 0) {
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  text: updated[updated.length - 1].text + event.token
                }
              }
              return updated
            })
          }

          if (event.type === 'result') {
            setResult(event)
            activeNodeRef.current = null
          }

          if (event.type === 'error') throw new Error(event.message)
        }
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setRunning(false)
      activeNodeRef.current = null
    }
  }

  return (
    <div className="app">
      <header>
        <h1>⚖️ Debate Arena</h1>
        <p className="subtitle">Multi-agent debate with memory — Pro vs Con</p>
      </header>

      <form className="form" onSubmit={handleDebate}>
        <input
          className="topic-input"
          placeholder="Enter a debate topic…"
          value={topic}
          onChange={e => setTopic(e.target.value)}
          disabled={running}
        />
        <button className="debate-btn" type="submit" disabled={running || topic.trim().length < 3}>
          {running ? <span className="spinner" /> : 'Debate'}
        </button>
      </form>

      {error && <div className="error">⚠ {error}</div>}

      {status && (
        <div className="status-bar">
          <span className="status-dot" />
          {status}
        </div>
      )}

      {cards.length > 0 && (
        <div className="arguments">
          {Object.entries(
            cards.reduce((acc, c, i) => {
              const phase = c.round.replace(/^(pro|con)_/, '')
              if (!acc[phase]) acc[phase] = []
              acc[phase].push({ ...c, i })
              return acc
            }, {})
          ).map(([phase, pair]) => (
            <div key={phase} className="phase-row">
              {['pro', 'con'].map(side => {
                const c = pair.find(x => x.side.toLowerCase() === side)
                return c ? (
                  <ArgumentCard
                    key={c.round}
                    round={c.round}
                    side={c.side}
                    text={c.text}
                    active={running && c.i === cards.length - 1}
                  />
                ) : <div key={side} className="card-placeholder" />
              })}
            </div>
          ))}
        </div>
      )}

      {result && (
        <div className="moderator-wrap">
          <div className="moderator-card">
            <div className="moderator-header">
              <span>⚖️ Moderator's Verdict</span>
            </div>
            <div className="moderator-body">
              <div className="winner-label">🏆 Winner: {result.winner}</div>
              <pre className="summary">{result.summary}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
