# Phase 2: Tool Mastery — Function Calling, Structured Outputs & Error Handling

## What This Phase Covers

Phase 2 transforms you from "I can make an agent respond" to "I can make an agent **do things reliably**." You'll learn how LLMs actually invoke tools, how to force their outputs into predictable shapes, and how to handle the inevitable failures that come with real-world tool execution.

**Think of it this way**: In Phase 1, you learned that agents can call tools. In Phase 2, you learn how to make those tool calls **precise, validated, and resilient**.

---

## Prerequisites

Before starting Phase 2, you should be comfortable with:

- [x] What an agent is (vs a prompt vs a workflow)
- [x] The ReAct loop: Think → Decide → Tool Call → Observe → Loop
- [x] Basic tool calling with `@tool` decorator in LangChain
- [x] Raw HTTP calls to the Gemini API
- [x] Python basics: functions, classes, decorators, type hints
- [x] Basic Pydantic models (`BaseModel`)

**From your .NET background, you should know**: Dependency injection, interfaces, data annotations, middleware concept.

---

## Study Order (Strict — Do Not Skip Ahead)

```
01_function_calling.md        ← Start here. Foundation for everything.
        │
        ▼
02_structured_outputs.md      ← Builds on function calling schemas.
        │
        ▼
03_error_handling_and_retries.md  ← Makes everything production-ready.
        │
        ▼
glossary.md                   ← Review all terms after completing topics.
```

**Why this order?**
- Function calling teaches you how LLMs communicate with external tools — this is the **mechanism**.
- Structured outputs teach you how to control what comes back — this is the **contract**.
- Error handling teaches you what happens when things break — this is the **resilience**.

Each concept builds directly on the previous one. Structured outputs extend function calling schemas. Error handling wraps around both.

---

## Suggested Daily Breakdown (5–6 Hours/Day)

### Day 1: Function Calling Deep Dive (~5.5 hrs)

| Time | Activity | File |
|------|----------|------|
| 0:00–1:30 | Read and study function calling concepts (sections 1–5) | `01_function_calling.md` |
| 1:30–2:00 | Break — let concepts settle | — |
| 2:00–3:30 | Study sections 6–10, run all Python examples | `01_function_calling.md` |
| 3:30–4:00 | Break | — |
| 4:00–5:00 | Start structured outputs (sections 1–4) | `02_structured_outputs.md` |
| 5:00–5:30 | Review function calling glossary terms | `glossary.md` |

### Day 2: Structured Outputs + Error Handling (~5.5 hrs)

| Time | Activity | File |
|------|----------|------|
| 0:00–1:30 | Complete structured outputs (sections 5–10), run examples | `02_structured_outputs.md` |
| 1:30–2:00 | Break | — |
| 2:00–3:30 | Read error handling (sections 1–6) | `03_error_handling_and_retries.md` |
| 3:30–4:00 | Break | — |
| 4:00–5:00 | Complete error handling (sections 7–10), run examples | `03_error_handling_and_retries.md` |
| 5:00–5:30 | Full glossary review, cross-reference concepts | `glossary.md` |

---

## Key Outcomes

After completing Phase 2, you will be able to:

1. **Explain** how function calling works under the hood (not just use it)
2. **Design** tool schemas that LLMs can understand and use correctly
3. **Force** LLM outputs into Pydantic models with validation
4. **Handle** tool failures gracefully with retries, fallbacks, and circuit breakers
5. **Compare** framework-based (LangChain) vs raw (HTTP) approaches for each concept
6. **Map** every concept to its .NET equivalent for mental model building

---

## Common Traps

| Trap | Why It's Dangerous | How to Avoid |
|------|-------------------|--------------|
| Writing tool code before tool descriptions | The LLM reads descriptions, not code. Bad descriptions = bad tool usage. | Spend 80% of time on descriptions, 20% on implementation. |
| Over-engineering Pydantic schemas | Complex nested schemas confuse LLMs. | Start simple. Add complexity only when needed. |
| Ignoring partial failures | Tools can half-succeed (e.g., DB write succeeds but return parsing fails). | Always validate the full round-trip, not just the call. |
| Assuming retries always help | Some failures are permanent (auth, invalid input). Retrying wastes tokens. | Classify errors: retryable vs non-retryable. |
| Using structured outputs for everything | Free-form text is better for creative tasks. | Use structured output only when you need machine-readable results. |

---

## How This Connects to Your .NET Knowledge

| Phase 2 Concept | .NET Equivalent | Key Insight |
|----------------|----------------|-------------|
| Tool/Function Calling | `IService` resolved via DI | LLM "resolves" tools by name, like DI resolves by interface |
| Tool Schema | Interface definition + XML docs | The schema IS the contract between LLM and tool |
| Structured Output | Strongly-typed DTO + `[Required]` | Forces response into a known shape, like model binding |
| Pydantic Validation | FluentValidation / Data Annotations | Runtime enforcement of output constraints |
| Retry Logic | Polly `RetryPolicy` | Same exponential backoff, same idempotency concerns |
| Fallback Chains | Polly `FallbackPolicy` | Try primary → try secondary → return default |
| Circuit Breaker | Polly `CircuitBreakerPolicy` | Stop calling a broken tool after N failures |

---

## Files in This Phase

| File | Topic | Estimated Study Time |
|------|-------|---------------------|
| [01_function_calling.md](01_function_calling.md) | Deep dive into tool/function calling | ~3 hours |
| [02_structured_outputs.md](02_structured_outputs.md) | Pydantic, JSON schema, enforced outputs | ~3 hours |
| [03_error_handling_and_retries.md](03_error_handling_and_retries.md) | Failures, retries, fallbacks | ~3 hours |
| [glossary.md](glossary.md) | All Phase 2 terminology | ~30 min (review) |

**Total estimated study time: ~10 hours across 2 days**

---

## What Comes Next

Phase 3 builds on everything here. You'll use function calling to give agents tools, structured outputs to define agent communication protocols, and error handling to make multi-agent systems resilient. Without Phase 2 mastery, multi-agent systems will feel like magic you can't debug.
