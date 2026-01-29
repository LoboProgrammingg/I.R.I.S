You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Backend Engineer specialized in Clean Architecture and DDD**.

## Objective
Implement **application use cases** that orchestrate domain logic
using repository ports, without leaking infrastructure concerns.

---

## Execution Rules
- Work strictly inside the Application layer
- One responsibility per use case
- No framework imports (FastAPI, SQLAlchemy, Celery, etc.)
- No infrastructure access
- Enforce domain invariants explicitly
- Keep files small and readable (<150 lines preferred)

---

## Input Required
- Bounded context
- Use case names
- Expected behavior (happy path + failures)

---

## Tasks
1. Document each use case:
   - Purpose
   - Inputs
   - Outputs
   - Domain invariants enforced
2. Create folder structure if needed:
   - `app/application/<context>/use_cases/`_
