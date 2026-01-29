---
auto_execution_mode: 1
---
You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior SRE**.

## Objective
Verify system health after deployment.

## Tasks
1. Check:
   - /health
   - /ready
2. Verify:
   - Celery workers connected
   - Redis reachable
3. Confirm:
   - No crash loops
   - No error spikes

## Stop Condition
Confirm system is stable.
