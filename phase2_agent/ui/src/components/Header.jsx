export default function Header({ sessionId }) {
  const tools = [
    { icon: "⊞", label: "Calculator" },
    { icon: "⊙", label: "Search" },
    { icon: "⊟", label: "Database" },
  ];

  return (
    <header className="header glass">
      {/* Left — avatar + name + status */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div className="avatar">
          A
          <div className="avatar-ring" />
        </div>
        <div>
          <div className="agent-name">ReAct Agent</div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 3 }}>
            <span className="status-dot" />
            <span className="status-label">Online</span>
          </div>
        </div>
      </div>

      {/* Center — tool badges */}
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {tools.map(t => (
          <div key={t.label} className="tool-badge">
            <span style={{ fontSize: 12 }}>{t.icon}</span>
            {t.label}
          </div>
        ))}
      </div>

      {/* Right — session */}
      {sessionId ? (
        <div className="session-id">{sessionId.slice(0, 8)}</div>
      ) : (
        <div className="session-id">——</div>
      )}
    </header>
  );
}
