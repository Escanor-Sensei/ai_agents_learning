# Blog Generation Graph — Phase 3

## Main Graph

```mermaid
graph TD
    A[START] --> B[supervisor]
    B -->|no research| C[researcher]
    B -->|no outline| D[analyst]
    B -->|no blog| E[writer]
    B -->|quality ok| F[END]
    B -->|needs rework| E
    B -->|outline weak| D
    B -->|research shallow| C
    C --> B
    D --> B
    E --> B
```

## State Flow

```mermaid
graph LR
    A([topic]) --> B[Researcher]
    B -->|research_notes| C[Analyst]
    C -->|outline| D[Writer]
    D -->|blog_post| E{Supervisor}
    E -->|FINISH| F([blog_post])
    E -->|retry| B
    E -->|retry| C
    E -->|retry| D
    E -->|max retries| F
```

## Node Responsibilities

| Node | Reads | Writes |
|---|---|---|
| supervisor | entire state | next_node, supervisor_feedback, retry_count |
| researcher | topic, supervisor_feedback | research_notes |
| analyst | research_notes, supervisor_feedback | outline |
| writer | outline, research_notes, supervisor_feedback | blog_post |
