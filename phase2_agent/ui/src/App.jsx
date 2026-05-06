import { useState, useRef, useEffect, useCallback } from "react";
import axios from "axios";
import AnimatedBackground from "./components/AnimatedBackground";
import Header from "./components/Header";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import TypingIndicator from "./components/TypingIndicator";
import ConversationSidebar from "./components/ConversationSidebar";

const API_URL = "http://localhost:8000";
const USER_ID = localStorage.getItem("userId") ?? (() => {
  const id = crypto.randomUUID();
  localStorage.setItem("userId", id);
  return id;
})();

const WELCOME = {
  role: "assistant",
  content: "Hi! I'm your AI agent. I can help you with:\n• 🧮 Math calculations\n• 🔍 Web search\n• 🗄️ Database queries (PaymentDB)\n\nWhat would you like to know?",
};

export default function App() {
  const [messages, setMessages] = useState([WELCOME]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [sidebarLoading, setSidebarLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const fetchConversations = useCallback(async () => {
    setSidebarLoading(true);
    try {
      const { data } = await axios.get(`${API_URL}/conversations/${USER_ID}`);
      setConversations(data);
    } catch {
      // silently fail — sidebar is non-critical
    } finally {
      setSidebarLoading(false);
    }
  }, []);

  useEffect(() => {
    axios.post(`${API_URL}/users/ensure`, { user_id: USER_ID })
      .finally(() => fetchConversations());
  }, [fetchConversations]);

  const handleSelectConversation = async (conv) => {
    try {
      const { data } = await axios.get(`${API_URL}/conversations/${USER_ID}/${conv.conversation_id}/messages`);
      const loaded = data.map(m => ({
        role: m.role,
        content: m.content,
        toolCalls: m.tool_calls,
      }));
      setMessages(loaded.length ? loaded : [WELCOME]);
      setConversationId(conv.conversation_id);
      setSessionId(conv.session_id);
    } catch {
      setMessages([WELCOME]);
    }
  };

  const handleNewChat = () => {
    setMessages([WELCOME]);
    setSessionId(null);
    setConversationId(null);
  };

  const sendMessage = async (text) => {
    setMessages(prev => [...prev, { role: "user", content: text }]);
    setLoading(true);
    try {
      const { data } = await axios.post(`${API_URL}/chat`, {
        message: text,
        session_id: sessionId,
        conversation_id: conversationId,
        user_id: USER_ID,
      });
      setSessionId(data.session_id);
      setConversationId(data.conversation_id);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.reply,
        toolCalls: data.tool_calls,
        model: data.model,
      }]);
      fetchConversations(); // refresh sidebar
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
      <div className="layout">
        <ConversationSidebar
          conversations={conversations}
          activeId={conversationId}
          onSelect={handleSelectConversation}
          onNew={handleNewChat}
          loading={sidebarLoading}
        />
        <div className="chat-container">
          <Header sessionId={sessionId} />
          <div className="messages-area">
            {messages.map((msg, i) => (
              <ChatMessage key={i} role={msg.role} content={msg.content} toolCalls={msg.toolCalls} />
            ))}
            {loading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
          <ChatInput onSend={sendMessage} disabled={loading} />
        </div>
      </div>
    </div>
  );
}
