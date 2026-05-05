import { useState, useRef, useEffect } from "react";
import axios from "axios";
import AnimatedBackground from "./components/AnimatedBackground";
import Header from "./components/Header";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import TypingIndicator from "./components/TypingIndicator";

const API_URL = "http://localhost:8000";

const WELCOME = {
  role: "assistant",
  content: "Hi! I'm your AI agent. I can help you with:\n• 🧮 Math calculations\n• 🔍 Web search\n• 🗄️ Database queries (PaymentDB)\n\nWhat would you like to know?",
};

export default function App() {
  const [messages, setMessages] = useState([WELCOME]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text) => {
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setLoading(true);
    try {
      const { data } = await axios.post(`${API_URL}/chat`, { message: text });
      setSessionId(data.session_id);
      setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
    } catch (err) {
      const msg = err.response
        ? `Server error: ${err.response.status}`
        : "Cannot reach the agent. Is the API server running?";
      setMessages(prev => [...prev, { role: "assistant", content: `⚠️ ${msg}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-root">
      <AnimatedBackground />
      <div className="chat-container">
        <Header sessionId={sessionId} />
        <div className="messages-area">
          {messages.map((msg, i) => (
            <ChatMessage key={i} role={msg.role} content={msg.content} />
          ))}
          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>
        <ChatInput onSend={sendMessage} disabled={loading} />
      </div>
    </div>
  );
}
