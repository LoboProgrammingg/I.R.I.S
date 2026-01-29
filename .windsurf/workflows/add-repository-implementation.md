You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Backend Engineer specialized in infrastructure and persistence**.

## Objective
Implement repository infrastructure that adapts
domain entities to the database using ORM models,
strictly following Clean Architecture.

---

## Execution Rules
- Infrastructure layer only
- Implement existing repository ports
- No business logic
- No use cases
- No API
- No cross-bounded-context access

---

## Input Required
- Bounded context name
- Repository port(s) to implement

---

## Tasks
1. Create repository implementation file(s) under:
   `app/infrastructure/db/repositories/<context>.py`
2. Implement all methods defined in the port(s)
3. Map:
   - Domain entity → ORM model
   - ORM model → Domain entity
4. Use:
   - Async SQLAlchemy session
   - Explicit queries (no magic)
5. Ensure tenant isolation in all queries

---

## Constraints
- No implicit commits
- No lazy loading side effects
- No business rule enforcement
- Keep files small and readable (<150 lines preferred)

---

## Stop Condition
- Summarize repository behavior
- Explicitly state what is NOT handled
- Stop execution
- Ask for confirmation unless pre-authorized
