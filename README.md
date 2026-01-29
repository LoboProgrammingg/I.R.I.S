# IRIS - AI Billing System

WhatsApp-first AI finance assistant for automated boleto management.

## Architecture

- **Clean Architecture + DDD**
- **Python 3.12+**
- **FastAPI** - HTTP API
- **PostgreSQL** - Primary database
- **Redis** - Cache and Celery broker
- **Celery** - Background tasks
- **Alembic** - Database migrations

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Running with Docker

```bash
# Start all services
docker compose up -d

# Check logs
docker compose logs -f app

# Stop services
docker compose down
```

### Health Checks

- **Liveness:** `GET /health`
- **Readiness:** `GET /ready`

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format and lint
ruff check --fix .
ruff format .

# Type check
mypy app
```

## Project Structure

```
app/
├── config/          # Settings and logging
├── domain/          # Pure business logic (no external deps)
├── application/     # Use cases, ports, DTOs
├── infrastructure/  # DB, Redis, Celery, providers
└── interfaces/      # HTTP routers, webhooks
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IRIS_APP_ENV` | Environment (development/test/production) | development |
| `IRIS_DEBUG` | Enable debug mode | false |
| `IRIS_DATABASE_URL` | PostgreSQL connection string | - |
| `IRIS_REDIS_URL` | Redis connection string | - |
| `IRIS_CELERY_BROKER_URL` | Celery broker URL | - |
| `IRIS_CELERY_RESULT_BACKEND` | Celery result backend URL | - |

## Documentation

See `docs/phase-1-blueprint.md` for full architecture documentation.
