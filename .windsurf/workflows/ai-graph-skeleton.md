---
auto_execution_mode: 1
---
You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior AI Engineer**.

## Objective
Create a **minimal LangGraph skeleton** with no business logic.

## Tasks
1. Create AI folder structure:
   - ai/
     - graph.py
     - state.py
     - nodes/
2. Define:
   - Graph state model (Pydantic)
   - Node interfaces (empty or minimal)
3. Wire graph flow:
   - Explicit node ordering
   - No skipping allowed
4. Add inline comments explaining responsibilities.

## Constraints
- No business logic
- No external calls
- No DB access
- Files <150 lines

## Validation
- Graph can be instantiated
- Graph does nothing harmful
- Deterministic order enforced

## Stop Condition
Summarize structure and wait for approval to add nodes.
