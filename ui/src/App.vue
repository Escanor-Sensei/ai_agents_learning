<template>
  <div class="app">
    <!-- App Header -->
    <header class="app-header" role="banner">
      <div class="app-header__content">
        <h1 class="app-header__title">
          <span class="app-header__icon" aria-hidden="true">🤖</span>
          Smart Task Agent
        </h1>
        <p class="app-header__subtitle">Interactive Testing Interface - Day 1 Foundations</p>
      </div>
    </header>

    <!-- Main Layout -->
    <div class="app-layout">
      <AgentSidebar
        :agents="agents"
        :selected-agent-id="selectedAgent?.id"
        @select="handleAgentSelect"
      />

      <ChatArea
        :selected-agent="selectedAgent"
        :messages="messages"
        :is-loading="isLoading"
        :messages-container="messagesContainer"
        @send="handleSendMessage"
        @clear="handleClearChat"
      />
    </div>
  </div>
</template>

<script>
import { watch } from 'vue'
import AgentSidebar from './components/AgentSidebar.vue'
import ChatArea from './components/ChatArea.vue'
import { useAgents } from './composables/useAgents'
import { useChat } from './composables/useChat'

export default {
  name: 'App',
  components: {
    AgentSidebar,
    ChatArea
  },
  setup() {
    // Composables
    const { agents, selectedAgent, selectAgent } = useAgents()
    const {
      messages,
      isLoading,
      messagesContainer,
      addMessage,
      sendMessage,
      clearMessages
    } = useChat()

    /**
     * Handle agent selection
     */
    const handleAgentSelect = (agent) => {
      selectAgent(agent)
      clearMessages()
      addMessage(
        'system',
        'System',
        `**${agent.name}** selected.\n\n${agent.description}.\n\nType your message below to test this agent.`
      )
    }

    /**
     * Handle message send
     */
    const handleSendMessage = async (message) => {
      if (!selectedAgent.value) return
      await sendMessage(selectedAgent.value.file, message)
    }

    /**
     * Handle chat clear
     */
    const handleClearChat = () => {
      clearMessages()
      if (selectedAgent.value) {
        addMessage(
          'system',
          'System',
          `Chat cleared. **${selectedAgent.value.name}** is ready.`
        )
      }
    }

    // Watch for agent changes
    watch(selectedAgent, (newAgent) => {
      if (newAgent) {
        document.title = `${newAgent.name} - Smart Task Agent`
      } else {
        document.title = 'Smart Task Agent'
      }
    })

    return {
      agents,
      selectedAgent,
      messages,
      isLoading,
      messagesContainer,
      handleAgentSelect,
      handleSendMessage,
      handleClearChat
    }
  }
}
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* ==========================================================================
   App Header
   ========================================================================== */

.app-header {
  background: var(--surface-secondary);
  border-bottom: 1px solid var(--border);
  padding: var(--space-5) var(--space-6);
  flex-shrink: 0;
}

.app-header__content {
  max-width: 1400px;
  margin: 0 auto;
}

.app-header__title {
  font-size: var(--text-2xl);
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-1);
  color: var(--text-primary);
}

.app-header__icon {
  font-size: var(--text-4xl);
  line-height: 1;
}

.app-header__subtitle {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  margin-left: calc(var(--text-4xl) + var(--space-3));
}

/* ==========================================================================
   App Layout
   ========================================================================== */

.app-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

/* ==========================================================================
   Mobile Responsive
   ========================================================================== */

@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }

  .app-header {
    padding: var(--space-4);
  }

  .app-header__title {
    font-size: var(--text-xl);
  }

  .app-header__icon {
    font-size: var(--text-3xl);
  }

  .app-header__subtitle {
    font-size: var(--text-xs);
    margin-left: calc(var(--text-3xl) + var(--space-3));
  }
}

/* Ensure proper height inheritance */
@media (max-width: 768px) and (max-height: 600px) {
  .app-header {
    padding: var(--space-3);
  }
}
</style>
