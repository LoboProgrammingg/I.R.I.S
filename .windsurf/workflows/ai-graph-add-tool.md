You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior AI Platform Engineer**.

## Objective
Expose a system capability as a controlled AI tool.

## Input Required
- Tool name
- Use case
- Required parameters
- Safety constraints

## Tasks
1. Define tool contract:
   - Input schema
   - Output schema
2. Document:
   - Preconditions
   - Postconditions
   - Idempotency behavior
3. Implement tool wrapper:
   - Calls application layer only
4. Add usage restrictions to AI graph.

## Constraints
- No direct DB access
- No provider calls
- No business logic in tool

## Stop Condition
Ask for approval before allowing AI to use the tool.
