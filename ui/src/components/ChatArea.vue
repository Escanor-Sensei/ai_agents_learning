<template>
  <main class="chat-area" role="main">
    <!-- Empty State -->
    <div v-if="!selectedAgent" class="empty-state">
      <div class="empty-state__content">
        <div class="empty-state__icon" aria-hidden="true">🎯</div>
        <h2 class="empty-state__title">Welcome to Smart Task Agent</h2>
        <p class="empty-state__description">
          Select an agent from the sidebar to start testing
        </p>
      </div>
    </div>

    <!-- Chat Interface -->
    <div v-else class="chat">
      <!-- Agent Header -->
      <header class="chat__header">
        <div class="chat__header-content">
          <span class="chat__header-icon" aria-hidden="true">
            {{ selectedAgent.icon }}
          </span>
          <div class="chat__header-info">
            <h2 class="chat__header-title">{{ selectedAgent.name }}</h2>
            <p class="chat__header-desc">{{ selectedAgent.description }}</p>
          </div>
        </div>
        <button
          @click="$emit('clear')"
          class="button button--ghost"
          type="button"
          aria-label="Clear chat history"
        >
          Clear Chat
        </button>
      </header>

      <!-- Messages Container -->
      <div
        ref="messagesContainer"
        class="chat__messages"
        role="log"
        aria-live="polite"
        aria-atomic="false"
      >
        <!-- Empty Chat State -->
        <div v-if="messages.length === 0" class="empty-messages">
          <p class="empty-messages__text">
            No messages yet. Start a conversation with {{ selectedAgent.name }}.
          </p>
        </div>

        <!-- Message List -->
        <ChatMessage
          v-for="message in messages"
          :key="message.id"
          :message="message"
        />

        <!-- Loading Indicator -->
        <div v-if="isLoading" class="loading-indicator" aria-live="polite">
          <div class="loading-indicator__content">
            <div class="typing-dots" aria-label="Agent is typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <ChatInput
        v-model="userInput"
        @send="handleSend"
        :disabled="isLoading"
      />
    </div>
  </main>
</template>

<script>
import { ref } from 'vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'

export default {
  name: 'ChatArea',
  components: {
    ChatMessage,
    ChatInput
  },
  props: {
    selectedAgent: {
      type: Object,
      default: null
    },
    messages: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    messagesContainer: {
      type: Object,
      default: null
    }
  },
  emits: ['send', 'clear'],
  setup(props, { emit }) {
    const userInput = ref('')
    const messagesContainer = ref(null)

    const handleSend = (message) => {
      emit('send', message)
      userInput.value = ''
    }

    return {
      userInput,
      messagesContainer,
      handleSend
    }
  }
}
</script>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--surface-primary);
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}

.empty-state__content {
  text-align: center;
  max-width: 400px;
}

.empty-state__icon {
  font-size: 4rem;
  margin-bottom: var(--space-4);
  opacity: 0.8;
}

.empty-state__title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.empty-state__description {
  color: var(--text-tertiary);
  font-size: var(--text-base);
}

/* Chat Container */
.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Chat Header */
.chat__header {
  background: var(--surface-secondary);
  border-bottom: 1px solid var(--border);
  padding: var(--space-4) var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  flex-shrink: 0;
}

.chat__header-content {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.chat__header-icon {
  font-size: var(--text-3xl);
  flex-shrink: 0;
}

.chat__header-info {
  min-width: 0;
}

.chat__header-title {
  font-weight: 600;
  font-size: var(--text-base);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.chat__header-desc {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

/* Messages Area */
.chat__messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.empty-messages {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}

.empty-messages__text {
  color: var(--text-tertiary);
  text-align: center;
  font-size: var(--text-sm);
}

/* Loading Indicator */
.loading-indicator {
  display: flex;
  align-self: flex-start;
  max-width: 85%;
}

.loading-indicator__content {
  background: var(--surface-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  border: 1px solid var(--border);
}

.typing-dots {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typingBounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Button Styles */
.button {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: none;
}

.button--ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.button--ghost:hover {
  background: var(--surface-tertiary);
  border-color: var(--border-hover);
}

.button--ghost:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .chat__header {
    padding: var(--space-3) var(--space-4);
  }

  .chat__messages {
    padding: var(--space-4);
  }

  .empty-state__icon {
    font-size: 3rem;
  }

  .empty-state__title {
    font-size: var(--text-xl);
  }
}
</style>
