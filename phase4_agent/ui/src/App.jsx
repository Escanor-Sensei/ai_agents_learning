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

const ARGUMENT_NODES = new Set(['pro_opening', 'con_opening', 'pro_rebuttal', 'con_rebuttal', 'pro_closing', 'con_closing'])

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
  const [topic, setTopic]       = useState('')
  const [status, setStatus]     = useState('')
  const [cards, setCards]       = useState([])
  const [result, setResult]     = useState(null)
  const [running, setRunning]   = useState(false)
  const [error, setError]       = useState('')
  const [interrupt, setInterrupt] = useState(null)  // { thread_id }
  const activeNodeRef = useRef(null)

  async function streamFrom(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
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
        if (raw === '[DONE]') { setStatus(''); return }

        const event = JSON.parse(raw)

        if (event.type === 'label') {
          setStatus(event.text)
          activeNodeRef.current = event.node
          if (ARGUMENT_NODES.has(event.node))
            setCards(prev => [...prev, { round: event.node, side: event.node.startsWith('pro') ? 'Pro' : 'Con', text: '' }])
        }
        if (event.type === 'token') {
          setCards(prev => {
            const updated = [...prev]
            if (updated.length > 0)
              updated[updated.length - 1] = { ...updated[updated.length - 1], text: updated[updated.length - 1].text + event.token }
            return updated
          })
        }
        if (event.type === 'interrupt') {
          setInterrupt({ thread_id: event.thread_id })
          setStatus('')
          return
        }
        if (event.type === 'result') {
          setResult(event)
          activeNodeRef.current = null
        }
        if (event.type === 'error') throw new Error(event.message)
      }
    }
  }

  async function handleDebate(e) {
    e.preventDefault()
    if (topic.trim().length < 3) return
    setRunning(true)
    setError('')
    setCards([])
    setResult(null)
    setStatus('⏳ Preparing the debate...')
    setInterrupt(null)
    activeNodeRef.current = null
    try {
      await streamFrom(`${API}/debate/stream`, { topic })
    } catch (err) {
      setError(err.message)
    } finally {
      setRunning(false)
      activeNodeRef.current = null
    }
  }

  async function handleResume(decision) {
    const thread_id = interrupt.thread_id
    setInterrupt(null)
    setRunning(true)
    setError('')
    if (decision === 'redo') setCards(prev => prev.filter(c => !c.round.includes('closing')))
    try {
      await streamFrom(`${API}/debate/resume`, { thread_id, decision })
    } catch (err) {
      setError(err.message)
    } finally {
      setRunning(false)
      activeNodeRef.current = null
    }
  }

  return (
    <div className="app">
      <div className="sticky-top">
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
      </div>

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

      {interrupt && (
        <div className="human-review">
          <p>🧑 Closing round complete. What would you like to do?</p>
          <div className="human-review-btns">
            <button className="review-btn continue" onClick={() => handleResume('continue')}>✅ Continue to Verdict</button>
            <button className="review-btn redo" onClick={() => handleResume('redo')}>🔁 Redo Closing Round</button>
          </div>
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
