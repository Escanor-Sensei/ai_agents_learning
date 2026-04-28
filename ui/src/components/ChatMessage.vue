<template>
  <div
    :class="[
      'message',
      `message--${message.type}`
    ]"
    role="article"
    :aria-label="`${message.role} message`"
  >
    <div class="message__content">
      <div class="message__header">
        <span class="message__role">{{ message.role }}</span>
        <time class="message__time" :datetime="message.timestamp">
          {{ message.time }}
        </time>
      </div>
      <div
        class="message__text"
        v-html="formattedText"
      />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { formatMessage } from '../utils/formatters'

export default {
  name: 'ChatMessage',
  props: {
    message: {
      type: Object,
      required: true,
      validator: (msg) => {
        return msg.type && msg.role && msg.text !== undefined
      }
    }
  },
  setup(props) {
    const formattedText = computed(() => formatMessage(props.message.text))

    return {
      formattedText
    }
  }
}
</script>

<style scoped>
.message {
  display: flex;
  max-width: 85%;
  animation: messageSlideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message--user {
  align-self: flex-end;
}

.message--assistant,
.message--system,
.message--error {
  align-self: flex-start;
}

.message__content {
  width: 100%;
  background: var(--surface-secondary);
  border-radius: var(--radius-xl);
  padding: var(--space-4);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.message--user .message__content {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-inverse);
}

.message--error .message__content {
  background: var(--error-bg);
  border-color: var(--error);
}

.message--system .message__content {
  background: var(--info-bg);
  border-color: var(--info);
}

.message__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
  gap: var(--space-3);
}

.message__role {
  font-weight: 600;
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.message--user .message__role {
  color: var(--text-inverse);
  opacity: 0.9;
}

.message__time {
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  flex-shrink: 0;
}

.message--user .message__time {
  color: var(--text-inverse);
  opacity: 0.7;
}

.message__text {
  color: var(--text-primary);
  line-height: 1.6;
  word-wrap: break-word;
  font-size: var(--text-sm);
}

.message--user .message__text {
  color: var(--text-inverse);
}

/* Format code blocks */
.message__text :deep(pre) {
  background: var(--surface-primary);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: var(--space-2) 0;
}

.message__text :deep(code) {
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.9em;
}

.message__text :deep(strong) {
  font-weight: 600;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .message {
    max-width: 95%;
  }
}
</style>
