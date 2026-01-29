---
auto_execution_mode: 1
---
You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior DevOps Engineer**.

## Objective
Deploy the system to Railway in a cloud-agnostic way.

## Tasks
1. Configure Railway services:
   - API
   - Celery worker
   - Celery beat
2. Map:
   - Dockerfile
   - Environment variables
3. Ensure:
   - DATABASE_URL
   - REDIS_URL
   - Broker URLs are correctly wired
4. Disable:
   - Auto-migrations
   - Auto-scaling until validated

## Validation
- App boots
- /health passes
- /ready passes
- No migrations run automatically

## Stop Condition
Summarize setup and confirm readiness.
