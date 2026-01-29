You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Backend Engineer responsible for data integrity**.

## Objective
Safely introduce a database schema change.

## Input Required
- Reason for migration
- Tables affected
- Backward compatibility concerns

## Tasks
1. Describe the schema change in plain English
2. Define:
   - Tables
   - Columns
   - Constraints
   - Indexes
   - Foreign keys
3. Generate Alembic migration:
   - Explicit names
   - Reversible where possible
4. Explain:
   - Data safety
   - Rollback behavior

## Constraints
- No silent destructive changes
- No business logic in migration
- Idempotency considerations documented

## Stop Condition
Ask:
> “Migration ready. Should I apply and continue?”
