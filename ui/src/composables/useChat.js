import { ref, nextTick } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const REQUEST_TIMEOUT = 60000

/**
 * Chat management composable
 * Handles message state, API calls, and chat operations
 */
export function useChat() {
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const messagesContainer = ref(null)

  /**
   * Add a message to the chat
   */
  const addMessage = (type, role, text) => {
    messages.value.push({
      id: Date.now() + Math.random(),
      type,
      role,
      text,
      timestamp: new Date().toISOString(),
      time: new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    })
    scrollToBottom()
  }

  /**
   * Send message to agent API
   */
  const sendMessage = async (agentFile, message) => {
    if (!message?.trim()) return

    error.value = null
    addMessage('user', 'You', message)
    isLoading.value = true

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/execute`,
        {
          agent: agentFile,
          input: message.trim()
        },
        { timeout: REQUEST_TIMEOUT }
      )

      if (response.data?.output) {
        addMessage('assistant', agentFile.replace(/^\d+_/, '').replace('.py', ''), response.data.output)
      } else {
        throw new Error('Invalid response format')
      }
    } catch (err) {
      const errorMessage = extractErrorMessage(err)
      error.value = errorMessage
      addMessage('error', 'Error', errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear all messages
   */
  const clearMessages = () => {
    messages.value = []
    error.value = null
  }

  /**
   * Scroll chat to bottom
   */
  const scrollToBottom = () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  }

  /**
   * Extract user-friendly error message
   */
  const extractErrorMessage = (err) => {
    if (err.code === 'ECONNABORTED') {
      return 'Request timed out. The agent took too long to respond.'
    }
    if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
      return 'Cannot connect to server. Please ensure the backend is running on port 8000.'
    }
    return err.response?.data?.error || err.message || 'An unexpected error occurred.'
  }

  return {
    messages,
    isLoading,
    error,
    messagesContainer,
    addMessage,
    sendMessage,
    clearMessages,
    scrollToBottom
  }
}
