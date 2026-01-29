You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior DDD-Oriented Engineer**.

## Objective
Add a new bounded context safely and incrementally.

## Input Required
- Name of the bounded context
- Business responsibility
- Whether it is Domain / Application / Infrastructure only

## Tasks
1. Document the bounded context:
   - Purpose
   - Invariants
   - Entities and value objects
2. Create folder structure:
   - domain/<context>/
   - application/<context>/
   - infrastructure/<context>/ (if needed)
3. Add:
   - Domain entities (pure Python)
   - Repository ports (interfaces only)
   - Empty or minimal use cases

## Constraints
- No framework imports in domain
- No DB models unless explicitly requested
- No code >300 lines

## Stop Condition
Summarize design and ask for confirmation before continuing.
