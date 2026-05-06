import { useState } from "react";

function formatContent(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .split("\n")
    .map(line => `<p>${line.trim() === "" ? "&nbsp;" : line}</p>`)
    .join("");
}

const TOOL_ICONS = { calculator: "🧮", web_search: "🔍", db_query: "🗄️" };

function ToolCallsPanel({ toolCalls }) {
  const [open, setOpen] = useState(false);
  if (!toolCalls?.length) return null;

  return (
    <div className="tool-calls-panel">
      <button className="tool-calls-toggle" onClick={() => setOpen(o => !o)}>
        <span className="tool-calls-icons">
          {[...new Set(toolCalls.map(t => t.name))].map(name => (
            <span key={name}>{TOOL_ICONS[name] ?? "🔧"}</span>
          ))}
        </span>
        <span>{toolCalls.length} tool call{toolCalls.length > 1 ? "s" : ""}</span>
        <span className="tool-calls-chevron">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="tool-calls-list">
          {toolCalls.map((tc, i) => (
            <div key={i} className="tool-call-item">
              <div className="tool-call-header">
                <span>{TOOL_ICONS[tc.name] ?? "🔧"}</span>
                <span className="tool-call-name">{tc.name}</span>
              </div>
              <div className="tool-call-row">
                <span className="tool-call-label">in</span>
                <code className="tool-call-value">{tc.input}</code>
              </div>
              <div className="tool-call-row">
                <span className="tool-call-label">out</span>
                <code className="tool-call-value">{tc.output}</code>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ChatMessage({ role, content, toolCalls }) {
  const isUser = role === "user";

  return (
    <div className={`message-row ${isUser ? "user" : "agent"}`}>
      <div className={`msg-avatar ${isUser ? "user-av" : "agent-av"}`}>
        {isUser ? "U" : "A"}
      </div>
      {isUser ? (
        <div className="bubble user-bubble">{content}</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6, maxWidth: "72%" }}>
          <ToolCallsPanel toolCalls={toolCalls} />
          <div className="bubble agent-bubble">
            <div
              className="ai-content"
              dangerouslySetInnerHTML={{ __html: formatContent(content) }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
