You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Integration Engineer**.

## Objective
Integrate an external provider safely (Paytime, Messaging, etc.).

## Tasks
1. Define provider contract (port/interface)
2. Describe:
   - Request/response models
   - Error cases
   - Timeouts & retries
3. Implement:
   - Infrastructure adapter
   - Mock or stub for testing
4. Add:
   - Idempotency handling
   - Logging (no sensitive data)

## Constraints
- No provider calls in domain or controllers
- Provider must be swappable
- No hardcoded secrets

## Stop Condition
Ask for confirmation before wiring into use cases.
