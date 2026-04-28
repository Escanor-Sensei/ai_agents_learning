import { ref } from 'vue'

/**
 * Agent configuration data
 */
const AGENT_CONFIG = [
  {
    id: 'prompt',
    name: '01 - Prompt',
    icon: '💬',
    description: 'Single LLM call',
    file: '01_prompt.py'
  },
  {
    id: 'workflow',
    name: '02 - Workflow',
    icon: '🔄',
    description: 'Chained LLM calls',
    file: '02_workflow.py'
  },
  {
    id: 'agent',
    name: '03 - Agent',
    icon: '🤖',
    description: 'LLM-controlled loop',
    file: '03_agent.py'
  },
  {
    id: 'raw_prompt',
    name: '04 - Raw Prompt',
    icon: '⚡',
    description: 'Raw HTTP call',
    file: '04_raw_prompt.py'
  },
  {
    id: 'raw_agent',
    name: '05 - Raw Agent',
    icon: '🔧',
    description: 'Agent from scratch',
    file: '05_raw_agent_loop.py'
  },
  {
    id: 'first_agent',
    name: '06 - First Agent',
    icon: '🎯',
    description: 'Framework agent',
    file: '06_first_agent.py'
  },
  {
    id: 'raw_react',
    name: '07 - Raw ReAct',
    icon: '⚙️',
    description: 'Raw ReAct pattern',
    file: '07_raw_react.py'
  }
]

/**
 * Agent management composable
 */
export function useAgents() {
  const agents = ref(AGENT_CONFIG)
  const selectedAgent = ref(null)

  const selectAgent = (agent) => {
    selectedAgent.value = agent
  }

  const clearSelection = () => {
    selectedAgent.value = null
  }

  return {
    agents,
    selectedAgent,
    selectAgent,
    clearSelection
  }
}
