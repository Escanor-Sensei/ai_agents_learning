<template>
  <div class="chat-input">
    <div class="chat-input__container">
      <label for="message-input" class="sr-only">Type your message</label>
      <textarea
        id="message-input"
        ref="inputRef"
        v-model="localValue"
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.shift.exact="handleNewLine"
        @input="adjustHeight"
        :placeholder="placeholder"
        :disabled="disabled"
        :aria-label="ariaLabel"
        class="chat-input__field"
        rows="1"
      />
      <button
        @click="handleSend"
        :disabled="!canSend"
        :aria-label="sendButtonLabel"
        class="chat-input__button"
        type="button"
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
        </svg>
      </button>
    </div>
    <div v-if="hint" class="chat-input__hint">
      {{ hint }}
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick } from 'vue'

export default {
  name: 'ChatInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    placeholder: {
      type: String,
      default: 'Type your message...'
    },
    hint: {
      type: String,
      default: 'Press Enter to send, Shift+Enter for new line'
    }
  },
  emits: ['update:modelValue', 'send'],
  setup(props, { emit }) {
    const inputRef = ref(null)
    const localValue = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const canSend = computed(() => {
      return !props.disabled && localValue.value.trim().length > 0
    })

    const ariaLabel = computed(() => {
      return props.disabled ? 'Message input (disabled)' : 'Type your message'
    })

    const sendButtonLabel = computed(() => {
      return canSend.value ? 'Send message' : 'Send message (disabled)'
    })

    const handleSend = () => {
      if (canSend.value) {
        emit('send', localValue.value.trim())
        localValue.value = ''
        nextTick(() => adjustHeight())
      }
    }

    const handleNewLine = () => {
      localValue.value += '\n'
    }

    const adjustHeight = () => {
      if (inputRef.value) {
        inputRef.value.style.height = 'auto'
        inputRef.value.style.height = `${Math.min(inputRef.value.scrollHeight, 150)}px`
      }
    }

    const focus = () => {
      inputRef.value?.focus()
    }

    return {
      inputRef,
      localValue,
      canSend,
      ariaLabel,
      sendButtonLabel,
      handleSend,
      handleNewLine,
      adjustHeight,
      focus
    }
  }
}
</script>

<style scoped>
.chat-input {
  border-top: 1px solid var(--border);
  background: var(--surface-secondary);
  padding: var(--space-4) var(--space-6);
}

.chat-input__container {
  display: flex;
  gap: var(--space-3);
  align-items: flex-end;
  max-width: 1200px;
  margin: 0 auto;
}

.chat-input__field {
  flex: 1;
  background: var(--surface-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: var(--space-3) var(--space-4);
  color: var(--text-primary);
  resize: none;
  font-size: var(--text-sm);
  line-height: 1.5;
  transition: border-color 0.2s, box-shadow 0.2s;
  min-height: 44px;
}

.chat-input__field:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 3px var(--primary-focus);
}

.chat-input__field:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: var(--surface-tertiary);
}

.chat-input__field::placeholder {
  color: var(--text-tertiary);
}

.chat-input__button {
  background: var(--primary);
  color: var(--text-inverse);
  width: 48px;
  height: 48px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.chat-input__button:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.chat-input__button:active:not(:disabled) {
  transform: translateY(0);
}

.chat-input__button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.chat-input__button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chat-input__hint {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  text-align: center;
  margin-top: var(--space-2);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .chat-input {
    padding: var(--space-3) var(--space-4);
  }

  .chat-input__hint {
    display: none;
  }
}
</style>
