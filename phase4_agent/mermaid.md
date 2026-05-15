# Debate Graph

```mermaid
flowchart TD
    START --> load_memory
    load_memory --> pro_opening
    pro_opening --> con_opening
    con_opening --> moderator_route

    moderator_route -->|rebuttal| pro_rebuttal
    moderator_route -->|closing| pro_closing
    moderator_route -->|end| moderator

    pro_rebuttal --> con_rebuttal
    con_rebuttal --> moderator_route

    pro_closing --> con_closing
    con_closing --> moderator
    moderator --> END
```
