# Phase 4 Glossary — Stateful Agents (RAG, Vectors & Memory)

> Quick-reference for all terms introduced in Phase 4.  
> Each entry includes a one-line definition, a .NET analogy, and the file where it's covered in depth.

---

## RAG (Retrieval-Augmented Generation)

| Term | Definition | .NET Analogy | Covered In |
|---|---|---|---|
| **RAG** | A technique that retrieves relevant documents before generating an LLM response — "search then answer" | Full-text search service + response template | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Chunking** | Splitting large documents into smaller, embeddable pieces (typically 500–1000 characters) | String splitting for search indexing — like breaking a book into searchable sections | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Chunk overlap** | Repeating characters at chunk boundaries so context isn't lost between chunks | Sliding window with overlap — ensures nothing falls between the cracks | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Embedding** | Converting text into a fixed-size vector (array of numbers) that captures semantic meaning | `ML.NET FeaturizeText` — text → `float[]` feature vector | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Retrieval** | Finding the K most relevant document chunks for a given query using vector similarity search | `searchIndex.SearchAsync(query, topK: 5)` — finding matching documents | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Generation** | The LLM producing an answer using the retrieved context | String interpolation with search results → LLM API call | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Grounding** | Instructing the LLM to use ONLY the provided context and not hallucinate | Input validation — "only use data from this source, reject anything else" | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Reranking** | A second pass that re-scores retrieved documents for better relevance before sending to the LLM | Post-query business rules that re-sort search results | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Metadata filtering** | Narrowing search results using document properties (source, department, date) before or after vector search | `WHERE` clause in SQL / search facets in Azure AI Search | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **Document loader** | A component that reads files (PDF, HTML, CSV) and converts them into text documents with metadata | `File.ReadAllText()`, `StreamReader`, file parsers | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |
| **RecursiveCharacterTextSplitter** | LangChain's default chunker — splits on paragraph → line → sentence → word boundaries hierarchically | Cascading string split with fallback separators | [01_rag_fundamentals.md](./01_rag_fundamentals.md) |

## Vector Databases

| Term | Definition | .NET Analogy | Covered In |
|---|---|---|---|
| **Vector database** | A database optimized for storing vectors and performing fast similarity search | Azure AI Search / Elasticsearch with vector support | [02_vector_databases.md](./02_vector_databases.md) |
| **Vector** | An array of numbers (e.g., 768 floats) representing the meaning of a piece of text | `float[]` — a fixed-size numeric array | [02_vector_databases.md](./02_vector_databases.md) |
| **Similarity search** | Finding the K vectors closest to a query vector (nearest neighbors) | `OrderByDescending(CosineSimilarity).Take(k)` with HNSW index | [02_vector_databases.md](./02_vector_databases.md) |
| **Cosine similarity** | Distance metric measuring the angle between two vectors (1.0 = identical, 0.0 = unrelated) | Custom `IComparer<float[]>` comparing vector directions | [02_vector_databases.md](./02_vector_databases.md) |
| **Euclidean distance (L2)** | Distance metric measuring straight-line distance between vectors (0 = identical) | `Math.Sqrt(Sum((a-b)^2))` — Pythagorean distance | [02_vector_databases.md](./02_vector_databases.md) |
| **HNSW** | Hierarchical Navigable Small World — multi-layer graph index for fast approximate nearest-neighbor search | B-tree index but for vectors — hierarchical navigation for O(log n) lookup | [02_vector_databases.md](./02_vector_databases.md) |
| **IVF** | Inverted File Index — partitions vectors into clusters, searches only relevant clusters | Hash partitioning in a database — reduce search space by grouping | [02_vector_databases.md](./02_vector_databases.md) |
| **Collection** | A named group of vectors in a vector database (like a table in SQL) | Database table / Search index | [02_vector_databases.md](./02_vector_databases.md) |
| **Chroma** | Embedded (in-process) vector database — zero setup, file-based persistence | SQLite for vectors — lightweight, no server needed | [02_vector_databases.md](./02_vector_databases.md) |
| **FAISS** | Facebook AI Similarity Search — high-performance local vector search library | In-memory `List<T>` with O(log n) custom search | [02_vector_databases.md](./02_vector_databases.md) |
| **Pinecone** | Managed cloud vector database — auto-scaling, production-grade | Azure SQL Database / Cosmos DB — fully managed cloud service | [02_vector_databases.md](./02_vector_databases.md) |
| **pgvector** | PostgreSQL extension that adds vector storage and search to an existing Postgres database | Adding full-text search to an existing SQL Server database | [02_vector_databases.md](./02_vector_databases.md) |
| **Approximate nearest neighbor (ANN)** | Finding "close enough" nearest neighbors in O(log n) instead of exact nearest in O(n) | Approximate search vs exact match — trade tiny accuracy for massive speed | [02_vector_databases.md](./02_vector_databases.md) |

## Memory in Agents

| Term | Definition | .NET Analogy | Covered In |
|---|---|---|---|
| **Agent memory** | The system that manages what an agent remembers between interactions — makes stateless LLMs appear stateful | Application state management (cache + DB + session) | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Short-term memory** | Remembers the current conversation — recent messages kept in a buffer or window | `IMemoryCache` — fast, in-process, session-scoped | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Long-term memory** | Persistent facts stored across sessions in a vector database — retrieved by semantic relevance | `IDistributedCache` (Redis) + search index — persistent, cross-session | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Episodic memory** | Summaries of past conversation sessions — "what happened last Tuesday" | EF Core audit log / Event store — compressed history of interactions | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Buffer memory** | Store all conversation messages — simple but grows unbounded | `List<Message>` — append-only, no eviction | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Window memory** | Keep only the last K messages — fixed size, drops old messages | `IMemoryCache` with size limit / circular buffer | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Summary memory** | Periodically summarize old messages, keep summary + recent messages | Background service that compresses old log entries | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Fact extraction** | Using an LLM to pull key, storable facts from a conversation | Data extraction pipeline — parse unstructured input into structured records | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Memory injection** | Adding retrieved memories into the system prompt before an LLM call | Middleware that enriches `HttpContext` with user data from cache/DB | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Context builder** | Component that combines short-term + long-term + episodic memories into a single prompt context | Service that aggregates data from cache, DB, and search for a request | [03_memory_in_agents.md](./03_memory_in_agents.md) |
| **Context window** | The maximum number of tokens an LLM can process in a single call — all agent context must fit within this | `MaxRequestBodySize` in Kestrel — hard limit on input size | [03_memory_in_agents.md](./03_memory_in_agents.md) |

---

## Memory Type Selection Quick Reference

```
Short conversation (< 20 turns)?
  → Buffer memory — store everything

Long conversation (50+ turns)?
  → Window memory (recent) + Summary (compressed older context)

Need to remember users across sessions?
  → Long-term memory (vector-backed facts)

Need to reference past conversations?
  → Episodic memory (session summaries)

Production agent?
  → All three: Window + Long-term + Episodic
```

## Database Selection Quick Reference

```
Prototyping / learning?
  → Chroma (zero setup, embedded)

High-performance local search?
  → FAISS (fastest, GPU-capable)

Production SaaS?
  → Pinecone (managed) or Qdrant Cloud (managed)

Already using PostgreSQL?
  → pgvector extension
```

---

**Back to Phase 4**: [README.md](./README.md)  
**Back to Phase 3**: [../phase3/README.md](../phase3/README.md)

## Agent Frameworks

| Term | Definition | Covered In |
|---|---|---|
| **LangGraph** | A LangChain library for building stateful multi-agent systems as directed graphs with nodes, edges, and shared state | [04_agent_frameworks.md](./04_agent_frameworks.md) |
| **ADK (Agent Development Kit)** | Google's framework for building Gemini-native agents with automatic LLM-driven orchestration and Vertex AI deployment | [04_agent_frameworks.md](./04_agent_frameworks.md) |
| **StateGraph** | LangGraph's core class — a directed graph where nodes are agent functions and edges define execution flow | [04_agent_frameworks.md](./04_agent_frameworks.md) |
| **Conditional edges** | LangGraph edges that call a routing function to decide the next node dynamically at runtime | [04_agent_frameworks.md](./04_agent_frameworks.md) |
| **Agent Card** | A JSON descriptor at `/.well-known/agent.json` that advertises an A2A agent's name, capabilities, and endpoint | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **Sub-agent** | In ADK, a specialized agent that the root orchestrator can delegate tasks to | [04_agent_frameworks.md](./04_agent_frameworks.md) |

## Agent Evaluation

| Term | Definition | Covered In |
|---|---|---|
| **RAGAS** | A framework for evaluating RAG pipelines across 4 metrics: faithfulness, answer relevance, context precision, context recall | [05_agent_evaluation.md](./05_agent_evaluation.md) |
| **Faithfulness** | Evaluation metric: does the agent's answer use only information from the retrieved context? (0–1) | [05_agent_evaluation.md](./05_agent_evaluation.md) |
| **Answer relevance** | Evaluation metric: does the agent's answer actually address the user's question? (0–1) | [05_agent_evaluation.md](./05_agent_evaluation.md) |
| **LLM-as-judge** | Using a (stronger) LLM to evaluate the quality of another LLM's output — scalable alternative to human labeling | [05_agent_evaluation.md](./05_agent_evaluation.md) |
| **Golden dataset** | A curated set of question/answer pairs with known correct answers used as ground truth for evaluation | [05_agent_evaluation.md](./05_agent_evaluation.md) |
| **Task completion rate** | % of tasks the agent completes successfully end-to-end | [05_agent_evaluation.md](./05_agent_evaluation.md) |

## Debugging & Monitoring

| Term | Definition | Covered In |
|---|---|---|
| **LangSmith** | Observability platform by LangChain — automatically traces every LLM call, tool invocation, and agent step | [06_debugging_monitoring.md](./06_debugging_monitoring.md) |
| **Trace** | A complete execution record of one agent run — all nodes, LLM calls, inputs, outputs, and latencies nested hierarchically | [06_debugging_monitoring.md](./06_debugging_monitoring.md) |
| **Span** | A single unit within a trace — one LLM call, one tool call, or one node execution | [06_debugging_monitoring.md](./06_debugging_monitoring.md) |
| **@traceable** | LangSmith decorator that adds any custom Python function to the trace tree | [06_debugging_monitoring.md](./06_debugging_monitoring.md) |
| **LangSmith dataset** | A collection of input/output pairs stored in LangSmith used for running evaluation experiments | [06_debugging_monitoring.md](./06_debugging_monitoring.md) |

## Advanced Agentic Patterns

| Term | Definition | Covered In |
|---|---|---|
| **ReAct** | Reason + Act pattern — agent alternates between reasoning about what to do and calling tools, adapting based on observations | [07_advanced_patterns.md](./07_advanced_patterns.md) |
| **Tree of Thought (ToT)** | Generates multiple reasoning paths in parallel, scores each, and selects the best — improves complex reasoning quality | [07_advanced_patterns.md](./07_advanced_patterns.md) |
| **Retry + Fallback** | Error handling pattern: retry with corrected input on failure, fall back to a safe default when retries are exhausted | [07_advanced_patterns.md](./07_advanced_patterns.md) |
| **Exponential backoff** | Retry strategy where wait time doubles after each failure — prevents overwhelming a rate-limited API | [07_advanced_patterns.md](./07_advanced_patterns.md) |
| **Circuit breaker** | A guard that stops retrying after N failures — prevents infinite loops in agent pipelines | [07_advanced_patterns.md](./07_advanced_patterns.md) |

## Guardrails & Safety

| Term | Definition | Covered In |
|---|---|---|
| **Input guardrail** | A safety check applied to user input before it reaches the agent — blocks harmful, off-topic, or injected content | [08_guardrails_safety.md](./08_guardrails_safety.md) |
| **Output guardrail** | A safety check applied to agent output before it reaches the user — redacts PII, blocks harmful content | [08_guardrails_safety.md](./08_guardrails_safety.md) |
| **Prompt injection** | An attack where a user crafts input that overrides the agent's system prompt or hijacks its tool calls | [08_guardrails_safety.md](./08_guardrails_safety.md) |
| **PII redaction** | Automatically replacing personally identifiable information (email, phone, SSN) with placeholders before logging or returning | [08_guardrails_safety.md](./08_guardrails_safety.md) |
| **Scope enforcement** | Guardrail that rejects requests outside the agent's intended domain | [08_guardrails_safety.md](./08_guardrails_safety.md) |
| **Human-in-the-loop** | Requiring human approval before the agent executes high-risk or irreversible actions | [08_guardrails_safety.md](./08_guardrails_safety.md) |
| **Defense in depth** | Using multiple guardrail layers (rules + classifier + LLM judge) so no single layer is a single point of failure | [08_guardrails_safety.md](./08_guardrails_safety.md) |

## MCP & A2A Protocols

| Term | Definition | Covered In |
|---|---|---|
| **MCP (Model Context Protocol)** | Open standard by Anthropic for how agents connect to external tools and data sources via a client-server protocol | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **A2A (Agent-to-Agent)** | Open standard by Google for how agents communicate with and delegate tasks to other agents across systems | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **MCP server** | A process that exposes tools, resources, and prompts via the MCP protocol — can be used by any MCP client | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **MCP client** | An agent or application that connects to MCP servers to discover and call their tools | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **MCP tool** | A callable function exposed by an MCP server — equivalent to a LangChain `@tool` but framework-agnostic | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **MCP resource** | Data exposed by an MCP server that an agent can read (files, DB records, API responses) | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **stdio transport** | MCP communication over standard input/output — used for local MCP servers running as child processes | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
| **SSE transport** | MCP communication over HTTP Server-Sent Events — used for remote MCP servers | [09_mcp_a2a_protocols.md](./09_mcp_a2a_protocols.md) |
