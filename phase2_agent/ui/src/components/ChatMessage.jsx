function formatContent(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .split("\n")
    .map(line => `<p>${line.trim() === "" ? "&nbsp;" : line}</p>`)
    .join("");
}

export default function ChatMessage({ role, content }) {
  const isUser = role === "user";

  return (
    <div className={`message-row ${isUser ? "user" : "agent"}`}>
      <div className={`msg-avatar ${isUser ? "user-av" : "agent-av"}`}>
        {isUser ? "U" : "A"}
      </div>
      <div className={`bubble ${isUser ? "user-bubble" : "agent-bubble"}`}>
        {isUser ? (
          content
        ) : (
          <div
            className="ai-content"
            dangerouslySetInnerHTML={{ __html: formatContent(content) }}
          />
        )}
      </div>
    </div>
  );
}
