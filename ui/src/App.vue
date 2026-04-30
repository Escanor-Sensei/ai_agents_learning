<template>
  <div class="app">
    <!-- App Header -->
    <header class="app-header" role="banner">
      <div class="app-header__content">
        <h1 class="app-header__title">
          <span class="app-header__icon" aria-hidden="true">🤖</span>
          Agentic AI Course
        </h1>
        <p class="app-header__subtitle">Interactive Testing Interface</p>
      </div>
      <!-- Module Tabs -->
      <nav class="module-tabs" role="tablist" aria-label="Module selection">
        <button
          v-for="mod in modules"
          :key="mod.id"
          @click="handleModuleSelect(mod.id)"
          :class="['module-tab', { 'module-tab--active': activeModuleId === mod.id }]"
          :aria-selected="activeModuleId === mod.id"
          role="tab"
          type="button"
        >
          <span class="module-tab__icon" aria-hidden="true">{{ mod.icon }}</span>
          <span class="module-tab__name">{{ mod.shortName }}</span>
        </button>
      </nav>
    </header>

    <!-- Main Layout -->
    <div class="app-layout">
      <AgentSidebar
        :agents="agents"
        :agents-by-day="agentsByDay"
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
    const { modules, activeModule, activeModuleId, agents, agentsByDay, apiBaseUrl, selectedAgent, selectModule, selectAgent } = useAgents()
    const {
      messages,
      isLoading,
      messagesContainer,
      addMessage,
      sendMessage,
      clearMessages
    } = useChat()

    /**
     * Handle module tab switch
     */
    const handleModuleSelect = (moduleId) => {
      selectModule(moduleId)
      clearMessages()
      addMessage(
        'system',
        'System',
        `Switched to **${activeModule.value.name}**. Select an agent from the sidebar.`
      )
    }

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
      await sendMessage(selectedAgent.value.file, message, apiBaseUrl.value)
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
        document.title = `${newAgent.name} - ${activeModule.value.shortName}`
      } else {
        document.title = 'Agentic AI Course'
      }
    })

    return {
      modules,
      activeModule,
      activeModuleId,
      agents,
      agentsByDay,
      selectedAgent,
      messages,
      isLoading,
      messagesContainer,
      handleModuleSelect,
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
   Module Tabs
   ========================================================================== */

.module-tabs {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
  margin-left: calc(var(--text-4xl) + var(--space-3));
}

.module-tab {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.module-tab:hover {
  background: var(--surface-tertiary);
  color: var(--text-primary);
}

.module-tab--active {
  background: var(--primary);
  color: var(--text-inverse);
  border-color: var(--primary);
}

.module-tab--active:hover {
  background: var(--primary-hover);
  color: var(--text-inverse);
}

.module-tab__icon {
  font-size: var(--text-base);
  line-height: 1;
}

.module-tab__name {
  white-space: nowrap;
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

  .module-tabs {
    margin-left: 0;
    margin-top: var(--space-3);
  }

  .module-tab {
    padding: var(--space-2) var(--space-3);
    font-size: var(--text-xs);
  }
}

/* Ensure proper height inheritance */
@media (max-width: 768px) and (max-height: 600px) {
  .app-header {
    padding: var(--space-3);
  }
}
</style>
