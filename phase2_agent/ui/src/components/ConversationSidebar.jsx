import { useEffect, useRef } from "react";

export default function ConversationSidebar({ conversations, activeId, onSelect, onNew, loading }) {
  const listRef = useRef(null);

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - d) / 86400000);
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return d.toLocaleDateString("en-US", { weekday: "long" });
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  // Group conversations by date label
  const grouped = conversations.reduce((acc, conv) => {
    const label = formatDate(conv.created_at);
    if (!acc[label]) acc[label] = [];
    acc[label].push(conv);
    return acc;
  }, {});

  return (
    <aside className="sidebar glass">
      <div className="sidebar-header">
        <span className="sidebar-title">Chats</span>
        <button className="new-chat-btn" onClick={onNew} title="New chat">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </button>
      </div>

      <div className="sidebar-list" ref={listRef}>
        {loading && <div className="sidebar-empty">Loading...</div>}
        {!loading && conversations.length === 0 && (
          <div className="sidebar-empty">No conversations yet</div>
        )}
        {Object.entries(grouped).map(([label, convs]) => (
          <div key={label}>
            <div className="sidebar-date-label">{label}</div>
            {convs.map(conv => (
              <button
                key={conv.conversation_id}
                className={`sidebar-item ${conv.conversation_id === activeId ? "active" : ""}`}
                onClick={() => onSelect(conv)}
              >
                <span className="sidebar-item-title">{conv.title}</span>
              </button>
            ))}
          </div>
        ))}
      </div>
    </aside>
  );
}
