---
auto_execution_mode: 1
---
You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Reliability Engineer**.

## Objective
Add an audit/logging node to the AI graph.

## Tasks
1. Implement audit node:
   - Records decisions
   - Records tool usage
2. Ensure:
   - No PII in logs
   - Correlation IDs included
3. Wire node as terminal step.

## Constraints
- No business logic
- No sensitive data

## Stop Condition
Confirm audit coverage.
