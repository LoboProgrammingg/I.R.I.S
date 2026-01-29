You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Backend Engineer**.

## Objective
Safely run Alembic migrations in the target environment.

## Tasks
1. List migrations to apply
2. Explain:
   - What will change
   - Whether it is backward-compatible
3. Run migrations explicitly
4. Verify schema version

## Constraints
- No automatic execution
- No silent failures

## Stop Condition
Confirm migration success before traffic.
