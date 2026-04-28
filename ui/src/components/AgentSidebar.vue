<template>
  <aside class="sidebar" role="navigation" aria-label="Agent selection">
    <div class="sidebar-section">
      <h2 class="sidebar-title">Select Agent</h2>
      <nav class="agent-list" role="list">
        <button
          v-for="agent in agents"
          :key="agent.id"
          @click="$emit('select', agent)"
          :class="['agent-button', { 'agent-button--active': isSelected(agent.id) }]"
          :aria-pressed="isSelected(agent.id)"
          :aria-label="`${agent.name}: ${agent.description}`"
          type="button"
        >
          <span class="agent-button__icon" aria-hidden="true">{{ agent.icon }}</span>
          <div class="agent-button__content">
            <div class="agent-button__name">{{ agent.name }}</div>
            <div class="agent-button__desc">{{ agent.description }}</div>
          </div>
        </button>
      </nav>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'AgentSidebar',
  props: {
    agents: {
      type: Array,
      required: true
    },
    selectedAgentId: {
      type: String,
      default: null
    }
  },
  emits: ['select'],
  methods: {
    isSelected(id) {
      return this.selectedAgentId === id
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  background: var(--surface-secondary);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: var(--space-6);
  flex-shrink: 0;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.sidebar-title {
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-tertiary);
}

.agent-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.agent-button {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  background: transparent;
  border-radius: var(--radius-lg);
  text-align: left;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--text-secondary);
  border: 1px solid transparent;
}

.agent-button:hover {
  background: var(--surface-tertiary);
  border-color: var(--border-hover);
}

.agent-button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.agent-button--active {
  background: var(--primary);
  color: var(--text-inverse);
  border-color: var(--primary);
}

.agent-button--active:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
}

.agent-button__icon {
  font-size: var(--text-2xl);
  flex-shrink: 0;
  line-height: 1;
}

.agent-button__content {
  flex: 1;
  min-width: 0;
}

.agent-button__name {
  font-weight: 600;
  font-size: var(--text-sm);
  margin-bottom: var(--space-1);
}

.agent-button__desc {
  font-size: var(--text-xs);
  opacity: 0.85;
  line-height: 1.4;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border);
    max-height: 40vh;
  }
}
</style>
