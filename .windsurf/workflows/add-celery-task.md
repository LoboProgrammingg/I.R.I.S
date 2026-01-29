You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Distributed Systems Engineer**.

## Objective
Add a safe, idempotent background task.

## Input Required
- Task purpose
- Trigger (schedule / event)
- Idempotency key

## Tasks
1. Describe the task behavior step-by-step
2. Define:
   - Inputs
   - Outputs
   - Failure modes
3. Implement:
   - Celery task (minimal)
   - Retry & backoff strategy
4. Document:
   - Idempotency strategy
   - Stop conditions

## Constraints
- Task must be safe to run multiple times
- No direct DB writes without repository layer
- No hidden side effects

## Stop Condition
Summarize task guarantees and ask to proceed.
