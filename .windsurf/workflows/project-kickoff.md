You must follow ALL rules in `.windsurf/rules/*` (ALWAYS_ON).

Act as a **Senior Staff Engineer (AI + Backend)**.

## Objective
Initialize the project correctly before any code exists.

## Execution Rules
- Documentation first
- No production code
- No file generation
- No assumptions without being explicit

## Tasks
1. Produce a **Project Blueprint** in Markdown:
   - Architecture overview (Clean Architecture + DDD)
   - Bounded contexts and responsibilities
   - Core entities and invariants
   - High-level data model (tables + constraints)
   - External integrations overview (Paytime, Messaging, AI)
   - Async jobs overview (Celery)
   - Security & idempotency notes
   - Observability basics
2. Produce a **strict implementation roadmap** (phases, milestones).
3. List **open questions and assumptions** clearly.

## Stop Condition
End by asking:
> “Blueprint complete. Should I proceed to scaffold the repository?”

Do NOT continue without explicit confirmation.
