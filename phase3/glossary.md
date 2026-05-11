# Phase 3 Glossary — Multi-Agent Systems

> Quick-reference for all terms introduced in Phase 3.  
> Each entry includes a one-line definition, a .NET analogy, and the file where it's covered in depth.

---

## Agent Roles & Architecture

| Term | Definition | .NET Analogy | Covered In |
|---|---|---|---|
| **Agent Role** | A specialized persona assigned to an LLM through its system prompt, defining what it should focus on and how it should behave | Service with a specific responsibility in DI (e.g., `IPaymentService`) | [01_agent_roles.md](./01_agent_roles.md) |
| **Planner Agent** | An agent responsible for breaking a task into sub-steps before execution begins | `MediatR` command handler that creates a plan/pipeline | [01_agent_roles.md](./01_agent_roles.md) |
| **Executor Agent** | An agent that carries out specific steps — uses tools, writes code, queries databases | Worker service / Background job processor | [01_agent_roles.md](./01_agent_roles.md) |
| **Critic Agent** | An agent that reviews output from other agents for quality, accuracy, or completeness | Validation middleware / `FluentValidation` pipeline behavior | [01_agent_roles.md](./01_agent_roles.md) |
| **Role Prompt** | A system prompt that defines an agent's identity, expertise, constraints, and output format | Interface contract (`IMyService`) that defines what a service does | [01_agent_roles.md](./01_agent_roles.md) |
| **Hybrid Role** | An agent that combines two or more roles (e.g., planner + executor for simple tasks) | A service that implements multiple interfaces | [01_agent_roles.md](./01_agent_roles.md) |

## Sequential Communication

| Term | Definition | .NET Analogy | Covered In |
|---|---|---|---|
| **Sequential Pipeline** | A fixed chain of agents where output from one feeds into the next (A → B → C) | ASP.NET middleware pipeline / `Chain of Responsibility` pattern | [02_sequential_communication.md](./02_sequential_communication.md) |
| **Context Passing** | How information flows between agents in a pipeline — can pass full output, accumulated context, or summaries | `HttpContext` flowing through middleware; each middleware reads and enriches it | [02_sequential_communication.md](./02_sequential_communication.md) |
| **Pass-Previous Strategy** | Each agent only sees the previous agent's output (not the full history) | Middleware that only reads `context.Request`, not the full pipeline state | [02_sequential_communication.md](./02_sequential_communication.md) |
| **Accumulate Strategy** | Each agent sees all previous agents' outputs concatenated | Middleware that reads the full `HttpContext.Items` dictionary | [02_sequential_communication.md](./02_sequential_communication.md) |
| **Summarize Strategy** | An intermediate step summarizes accumulated context before passing it on, to avoid context window overflow | Response compression middleware — reduces data before the next handler | [02_sequential_communication.md](./02_sequential_communication.md) |
| **Data Transformation** | Reshaping one agent's output format to match the next agent's expected input | DTO mapping with AutoMapper between service layers | [02_sequential_communication.md](./02_sequential_communication.md) |

## Hierarchical Systems

| Term | Definition | .NET Analogy | Covered In |
|---|---|---|---|
| **Supervisor** | A coordinating agent that receives tasks and delegates to sub-agents dynamically | Orchestrator service / API Gateway that routes requests to microservices | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Sub-Agent** | A specialized agent that the supervisor delegates work to — it does the actual work | A microservice called by the orchestrator | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Routing** | The supervisor's decision about which sub-agent should handle a given sub-task | Request routing in API Gateway / MVC controller action selection | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Routing Decision** | A structured output from the supervisor specifying: which agent, what task, and why | Route table entry / endpoint resolution result | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Agent Registry** | A collection of available sub-agents with their names, descriptions, and capabilities | DI container / Service collection where services are registered and resolved | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Delegation** | The act of the supervisor sending a specific task to a chosen sub-agent | `provider.GetRequiredService<T>()` — resolve and call a registered service | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Re-delegation** | Sending work back to a sub-agent with revised instructions when quality is insufficient | Retry policy in Polly — retry the service call with different parameters | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Max Iterations** | A safety limit on how many delegation rounds the supervisor can perform | Circuit breaker / timeout policy preventing infinite loops | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |
| **Dynamic Routing** | Supervisor determines the route at runtime (LLM decides) rather than following a fixed path | Convention-based routing in ASP.NET where routes are resolved from controller names | [03_hierarchical_agents.md](./03_hierarchical_agents.md) |

## Collaborative Patterns

| Term | Definition | .NET Analogy | Covered In |
|---|---|---|---|
| **Collaborative Pattern** | Multi-agent pattern where agents work as peers, sharing context and building on each other's work | Event-driven microservices communicating via event bus (MassTransit/NServiceBus) | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |
| **Debate Pattern** | Two or more agents argue opposing positions on a topic; a moderator evaluates and decides | Strategy pattern with multiple implementations + evaluation service | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |
| **Round-Robin** | Agents take turns contributing to a shared artifact, each seeing the full current state | Observer/Enricher pattern — multiple services enrich a shared model in turn | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |
| **Blackboard Pattern** | A shared state (blackboard) that all agents can read from and write to independently | Shared Redis cache + event-driven services; `ConcurrentDictionary` as shared state | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |
| **Moderator** | A neutral agent that evaluates the output of collaborating agents and makes a decision | Aggregator service / Decision engine that evaluates multiple service responses | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |
| **Consensus** | A mechanism for resolving disagreements among agents (voting, moderator, weighted vote, synthesis) | Distributed consensus / Saga completion step | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |
| **Shared Context** | Information visible to all participating agents in a collaborative pattern | Distributed cache / Event store that all services read from | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |
| **Mode Collapse** | When a single agent converges on one answer and reinforces it without exploring alternatives | A single service returning the same result regardless of input variation | [04_collaborative_patterns.md](./04_collaborative_patterns.md) |

## Cross-Cutting Concepts

| Term | Definition | .NET Analogy |
|---|---|---|
| **Context Window** | The maximum amount of text an LLM can process in a single call — all agent context must fit within this | Request size limit / `MaxRequestBodySize` in Kestrel |
| **Orchestration** | Coordinating multiple agents to accomplish a complex task — sequential, hierarchical, or collaborative | Saga orchestration / Workflow engine (e.g., Elsa, Durable Functions) |
| **State Management** | Tracking task progress, agent results, and decisions across multiple agent interactions | Saga state / Workflow state machine / `IDistributedCache` |
| **Agent Communication** | How agents exchange information — through messages, shared state, or tool calls | Service-to-service communication (HTTP, gRPC, event bus) |

---

## Pattern Selection Quick Reference

```
Task is simple, fixed order?
  → Sequential Pipeline (02)

Task needs dynamic routing to specialists?
  → Hierarchical Supervisor (03)

Task needs diverse perspectives or debate?
  → Collaborative Pattern (04)

Not sure?
  → Start with Hierarchical — it's the most flexible single pattern
```

---

**Back to Phase 3**: [README.md](./README.md)
