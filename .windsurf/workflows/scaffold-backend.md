You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Backend Engineer**.

## Objective
Create the initial backend scaffold with best-in-class practices.

## Constraints
- No business/domain logic yet
- Keep files minimal (<150 lines preferred)
- Python 3.12+
- Clean Architecture folder structure

## Tasks
1. Create repository structure:
   - app/
   - tests/
   - docker/
2. Generate:
   - `pyproject.toml` (ruff, black, basic config)
   - `Dockerfile`
   - `docker-compose.yml` (app + postgres + redis)
3. Create:
   - Minimal FastAPI app
   - `/health` and `/ready` endpoints
4. Initialize:
   - SQLAlchemy session (no models yet)
   - Alembic (empty migrations folder)
   - Celery app (no tasks yet)

## Validation
- `docker compose up` must start all services
- No unused dependencies
- No premature abstractions

## Stop Condition
Summarize what was created and ask:
> “Scaffold ready. Should I proceed to the first bounded context?”
