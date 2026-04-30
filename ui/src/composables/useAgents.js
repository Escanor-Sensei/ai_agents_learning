import { ref, computed } from 'vue'

/**
 * Module definitions — each module has its own agents, day labels, and API port
 */
const MODULES = {
  'smart-task-agent': {
    id: 'smart-task-agent',
    name: 'Module 1: Smart Task Agent',
    shortName: 'Smart Task Agent',
    icon: '🧠',
    port: 8000,
    dayLabels: {
      1: 'Day 1: Foundations',
      2: 'Day 2: Tools & Planning',
      3: 'Day 3: Memory & Reflection',
      4: 'Day 4: Production',
    },
    agents: [
      // Day 1: Foundations
      { id: 'd1_01_prompt', name: '01 - Prompt', icon: '💬', description: 'Single LLM call', file: 'day1/01_prompt.py', day: 1 },
      { id: 'd1_02_workflow', name: '02 - Workflow', icon: '🔄', description: 'Chained LLM calls', file: 'day1/02_workflow.py', day: 1 },
      { id: 'd1_03_agent', name: '03 - Agent', icon: '🤖', description: 'LLM-controlled loop', file: 'day1/03_agent.py', day: 1 },
      { id: 'd1_04_raw_prompt', name: '04 - Raw Prompt', icon: '⚡', description: 'Raw HTTP call', file: 'day1/04_raw_prompt.py', day: 1 },
      { id: 'd1_05_raw_agent', name: '05 - Raw Agent', icon: '🔧', description: 'Agent from scratch', file: 'day1/05_raw_agent_loop.py', day: 1 },
      { id: 'd1_06_first_agent', name: '06 - First Agent', icon: '🎯', description: 'Framework agent', file: 'day1/06_first_agent.py', day: 1 },
      { id: 'd1_07_raw_react', name: '07 - Raw ReAct', icon: '⚙️', description: 'Raw ReAct pattern', file: 'day1/07_raw_react.py', day: 1 },
      // Day 2: Tools & Planning
      { id: 'd2_01_real_tools', name: '01 - Real Tools', icon: '🛠️', description: '5 real tools + agent', file: 'day2/01_real_tools.py', day: 2 },
      { id: 'd2_02_tool_schemas', name: '02 - Tool Schemas', icon: '📋', description: 'How LLMs choose tools', file: 'day2/02_tool_schemas.py', day: 2 },
      { id: 'd2_03_raw_registry', name: '03 - Raw Registry', icon: '🔧', description: 'Manual tool dispatch', file: 'day2/03_raw_tool_registry.py', day: 2 },
      { id: 'd2_04_dynamic', name: '04 - Dynamic Select', icon: '🎯', description: '7 tools auto-routing', file: 'day2/04_dynamic_selection.py', day: 2 },
      { id: 'd2_05_planning', name: '05 - Planning', icon: '📝', description: 'Plan-then-Execute vs ReAct', file: 'day2/05_planning_intro.py', day: 2 },
      { id: 'd2_06_raw_planning', name: '06 - Raw Planning', icon: '⚡', description: 'Raw two-phase planning', file: 'day2/06_raw_planning.py', day: 2 },
      { id: 'd2_07_task', name: '07 - Task: Planner', icon: '🏗️', description: 'Build a planning agent', file: 'day2/07_task_build_planner.py', day: 2 },
      { id: 'd2_08_debug', name: '08 - Predict & Debug', icon: '🐛', description: 'Tool debugging exercises', file: 'day2/08_predict_debug.py', day: 2 },
      { id: 'd2_09_solution', name: '09 - Solution', icon: '✅', description: 'Planner solution', file: 'day2/09_reference_solution.py', day: 2 },
      // Day 3: Memory & Reflection
      { id: 'd3_01_short_mem', name: '01 - Short-Term Memory', icon: '🧠', description: 'Conversation context', file: 'day3/01_short_term_memory.py', day: 3 },
      { id: 'd3_02_raw_short', name: '02 - Raw Short-Term', icon: '⚡', description: 'Raw conversation memory', file: 'day3/02_raw_short_term.py', day: 3 },
      { id: 'd3_03_long_mem', name: '03 - Long-Term Memory', icon: '💾', description: 'Persistent JSON memory', file: 'day3/03_long_term_memory.py', day: 3 },
      { id: 'd3_04_raw_long', name: '04 - Raw Long-Term', icon: '🔧', description: 'Raw persistent memory', file: 'day3/04_raw_long_term.py', day: 3 },
      { id: 'd3_05_reflection', name: '05 - Reflection', icon: '🪞', description: 'Self-evaluation loop', file: 'day3/05_reflection.py', day: 3 },
      { id: 'd3_06_raw_reflect', name: '06 - Raw Reflection', icon: '⚡', description: 'Raw reflection loop', file: 'day3/06_raw_reflection.py', day: 3 },
      { id: 'd3_07_task', name: '07 - Task: Memory', icon: '🏗️', description: 'Build memory + reflection', file: 'day3/07_task_build_memory.py', day: 3 },
      { id: 'd3_08_debug', name: '08 - Predict & Debug', icon: '🐛', description: 'Memory debug exercises', file: 'day3/08_predict_debug.py', day: 3 },
      { id: 'd3_09_solution', name: '09 - Solution', icon: '✅', description: 'Memory agent solution', file: 'day3/09_reference_solution.py', day: 3 },
      // Day 4: Production & Integration
      { id: 'd4_01_full_agent', name: '01 - Full Agent', icon: '🤖', description: 'Framework complete agent', file: 'day4/01_full_agent.py', day: 4 },
      { id: 'd4_02_raw_full', name: '02 - Raw Full Agent', icon: '⚡', description: 'Raw complete agent', file: 'day4/02_raw_full_agent.py', day: 4 },
      { id: 'd4_03_logging', name: '03 - Logging & Trace', icon: '📊', description: 'Step-by-step tracing', file: 'day4/03_logging_trace.py', day: 4 },
      { id: 'd4_04_errors', name: '04 - Error Handling', icon: '🛡️', description: 'Retry, backoff, stuck detect', file: 'day4/04_error_handling.py', day: 4 },
      { id: 'd4_05_eval', name: '05 - Evaluation', icon: '📈', description: 'Test suite + scoring', file: 'day4/05_evaluation.py', day: 4 },
      { id: 'd4_06_comparison', name: '06 - FW vs Raw', icon: '⚖️', description: 'Side-by-side comparison', file: 'day4/06_framework_comparison.py', day: 4 },
      { id: 'd4_07_task', name: '07 - Task: Final Agent', icon: '🏗️', description: 'Build capstone agent', file: 'day4/07_task_final_agent.py', day: 4 },
      { id: 'd4_08_debug', name: '08 - Predict & Debug', icon: '🐛', description: 'Final debug exercises', file: 'day4/08_predict_debug.py', day: 4 },
      { id: 'd4_09_solution', name: '09 - Solution', icon: '✅', description: 'Complete agent solution', file: 'day4/09_reference_solution.py', day: 4 },
      { id: 'd4_10_next', name: '10 - What\'s Next', icon: '🚀', description: 'Roadmap & resources', file: 'day4/10_whats_next.py', day: 4 },
    ],
  },
  'action-agent': {
    id: 'action-agent',
    name: 'Module 2: Action Agent',
    shortName: 'Action Agent',
    icon: '⚡',
    port: 8001,
    dayLabels: {
      1: 'Day 1: Structured Output',
      2: 'Day 2: SQLite Database',
      3: 'Day 3: HTTP APIs & Composition',
      4: 'Day 4: Capstone Agent',
    },
    agents: [
      // Day 1: Structured Output & Parallel Calls
      { id: 'm2d1_01', name: '01 - JSON Mode', icon: '📋', description: 'LangChain structured output', file: 'day1/01_json_mode.py', day: 1 },
      { id: 'm2d1_02', name: '02 - Raw JSON', icon: '⚡', description: 'Gemini REST JSON schemas', file: 'day1/02_raw_json_mode.py', day: 1 },
      { id: 'm2d1_03', name: '03 - Pydantic Tools', icon: '🔧', description: 'Type-safe tool I/O', file: 'day1/03_pydantic_tools.py', day: 1 },
      { id: 'm2d1_04', name: '04 - Raw Validation', icon: '🛡️', description: 'Manual JSON validation', file: 'day1/04_raw_validation.py', day: 1 },
      { id: 'm2d1_05', name: '05 - Parallel Calls', icon: '⚡', description: 'Multiple tools at once', file: 'day1/05_parallel_calls.py', day: 1 },
      { id: 'm2d1_06', name: '06 - Raw Parallel', icon: '🔧', description: 'Raw parallel execution', file: 'day1/06_raw_parallel.py', day: 1 },
      { id: 'm2d1_07', name: '07 - Task: Extractor', icon: '🏗️', description: 'Build data extraction agent', file: 'day1/07_task_data_extractor.py', day: 1 },
      { id: 'm2d1_08', name: '08 - Predict & Debug', icon: '🐛', description: 'Schema debug exercises', file: 'day1/08_predict_debug.py', day: 1 },
      { id: 'm2d1_09', name: '09 - Solution', icon: '✅', description: 'Data extractor solution', file: 'day1/09_reference_solution.py', day: 1 },
      // Day 2: SQLite Database
      { id: 'm2d2_01', name: '01 - SQLite Basics', icon: '🗄️', description: 'LangChain DB tools', file: 'day2/01_sqlite_basics.py', day: 2 },
      { id: 'm2d2_02', name: '02 - Raw SQLite', icon: '⚡', description: 'Raw Gemini DB agent', file: 'day2/02_raw_sqlite.py', day: 2 },
      { id: 'm2d2_03', name: '03 - Schema Introspect', icon: '🔍', description: 'Auto-discover schema', file: 'day2/03_schema_introspection.py', day: 2 },
      { id: 'm2d2_04', name: '04 - Raw Schema', icon: '🔧', description: 'Raw 3-step pattern', file: 'day2/04_raw_schema_aware.py', day: 2 },
      { id: 'm2d2_05', name: '05 - Write Ops', icon: '✏️', description: 'INSERT/UPDATE/DELETE', file: 'day2/05_write_operations.py', day: 2 },
      { id: 'm2d2_06', name: '06 - Raw Writes', icon: '⚡', description: 'Raw writes + transactions', file: 'day2/06_raw_write_ops.py', day: 2 },
      { id: 'm2d2_07', name: '07 - Task: DB Agent', icon: '🏗️', description: 'Build complete DB agent', file: 'day2/07_task_db_assistant.py', day: 2 },
      { id: 'm2d2_08', name: '08 - Predict & Debug', icon: '🐛', description: 'SQL debug exercises', file: 'day2/08_predict_debug.py', day: 2 },
      { id: 'm2d2_09', name: '09 - Solution', icon: '✅', description: 'DB assistant solution', file: 'day2/09_reference_solution.py', day: 2 },
      // Day 3: HTTP APIs & Composition
      { id: 'm2d3_01', name: '01 - HTTP Tools', icon: '🌐', description: 'Weather + Wikipedia + FX', file: 'day3/01_http_tools.py', day: 3 },
      { id: 'm2d3_02', name: '02 - Raw HTTP', icon: '⚡', description: 'Raw API agent loop', file: 'day3/02_raw_http_tools.py', day: 3 },
      { id: 'm2d3_03', name: '03 - Composition', icon: '🔗', description: 'Chain DB → API calls', file: 'day3/03_tool_composition.py', day: 3 },
      { id: 'm2d3_04', name: '04 - Raw Compose', icon: '🔧', description: 'Manual data flow', file: 'day3/04_raw_composition.py', day: 3 },
      { id: 'm2d3_05', name: '05 - Fallback', icon: '🛡️', description: 'Resilient tool execution', file: 'day3/05_fallback_retry.py', day: 3 },
      { id: 'm2d3_06', name: '06 - Raw Fallback', icon: '⚡', description: 'Circuit breaker pattern', file: 'day3/06_raw_fallback.py', day: 3 },
      { id: 'm2d3_07', name: '07 - Task: Research', icon: '🏗️', description: 'Build research agent', file: 'day3/07_task_research_agent.py', day: 3 },
      { id: 'm2d3_08', name: '08 - Predict & Debug', icon: '🐛', description: 'API failure exercises', file: 'day3/08_predict_debug.py', day: 3 },
      { id: 'm2d3_09', name: '09 - Solution', icon: '✅', description: 'Research agent solution', file: 'day3/09_reference_solution.py', day: 3 },
      // Day 4: Capstone — The Action Agent
      { id: 'm2d4_01', name: '01 - Action Agent', icon: '🤖', description: 'Full company assistant', file: 'day4/01_action_agent.py', day: 4 },
      { id: 'm2d4_02', name: '02 - Raw Agent', icon: '⚡', description: 'Zero-framework agent', file: 'day4/02_raw_action_agent.py', day: 4 },
      { id: 'm2d4_03', name: '03 - Sanitization', icon: '🔒', description: 'SQL injection defense', file: 'day4/03_input_sanitization.py', day: 4 },
      { id: 'm2d4_04', name: '04 - Output Pipes', icon: '📊', description: 'Validate, truncate, redact', file: 'day4/04_output_pipelines.py', day: 4 },
      { id: 'm2d4_05', name: '05 - Eval Suite', icon: '📈', description: '12-query test suite', file: 'day4/05_eval_suite.py', day: 4 },
      { id: 'm2d4_06', name: '06 - Comparison', icon: '⚖️', description: 'Module 1 vs Module 2', file: 'day4/06_comparison.py', day: 4 },
      { id: 'm2d4_07', name: '07 - Task: Final', icon: '🏗️', description: 'Ultimate assistant task', file: 'day4/07_task_final_agent.py', day: 4 },
      { id: 'm2d4_08', name: '08 - Predict & Debug', icon: '🐛', description: 'Production failures', file: 'day4/08_predict_debug.py', day: 4 },
      { id: 'm2d4_09', name: '09 - Solution', icon: '✅', description: 'Complete agent solution', file: 'day4/09_reference_solution.py', day: 4 },
      { id: 'm2d4_10', name: '10 - Bridge', icon: '🚀', description: 'Preview Module 3', file: 'day4/10_bridge_multi_agent.py', day: 4 },
    ],
  },
}

/**
 * Agent management composable — supports multiple modules
 */
export function useAgents() {
  const activeModuleId = ref('smart-task-agent')
  const selectedAgent = ref(null)

  /** All module definitions */
  const modules = computed(() => Object.values(MODULES))

  /** Current active module */
  const activeModule = computed(() => MODULES[activeModuleId.value])

  /** Agents for the active module */
  const agents = computed(() => activeModule.value?.agents || [])

  /** API base URL for the active module */
  const apiBaseUrl = computed(() => `http://localhost:${activeModule.value?.port || 8000}`)

  /** Agents grouped by day for the active module */
  const agentsByDay = computed(() => {
    const mod = activeModule.value
    if (!mod) return []
    const groups = {}
    for (const agent of mod.agents) {
      const day = agent.day
      if (!groups[day]) {
        groups[day] = { day, label: mod.dayLabels[day] || `Day ${day}`, agents: [] }
      }
      groups[day].agents.push(agent)
    }
    return Object.values(groups).sort((a, b) => a.day - b.day)
  })

  const selectModule = (moduleId) => {
    activeModuleId.value = moduleId
    selectedAgent.value = null
  }

  const selectAgent = (agent) => {
    selectedAgent.value = agent
  }

  const clearSelection = () => {
    selectedAgent.value = null
  }

  return {
    modules,
    activeModule,
    activeModuleId,
    agents,
    agentsByDay,
    apiBaseUrl,
    selectedAgent,
    selectModule,
    selectAgent,
    clearSelection,
  }
}
