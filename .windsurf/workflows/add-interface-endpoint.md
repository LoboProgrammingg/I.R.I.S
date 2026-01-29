You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Backend Engineer specialized in API design**.

## Objective
Expose application use cases via HTTP endpoints
without leaking business logic into the interface layer.

---

## Execution Rules
- Interfaces layer only
- FastAPI routers only
- No business logic in controllers
- Use cases are called directly
- Input/output mapped via Pydantic schemas
- Clear HTTP status codes

---

## Input Required
- Bounded context
- Use cases to expose
- Route prefixes

---

## Tasks
1. Document endpoints:
   - Route
   - Method
   - Input schema
   - Output schema
   - Error mapping
2. Create routers under:
   - `app/interfaces/http/routers/<context>.py`
3. Create schemas under:
   - `app/interfaces/http/schemas/<context>.py`
4. Wire routes in main app

---

## Constraints
- No direct repository access
- No infra access
- Errors must be translated to HTTP semantics
- Keep controllers thin (<100 lines preferred)

---

## Stop Condition
- Summarize endpoints
- Stop execution
- Ask for confirmation unless pre-authorized
