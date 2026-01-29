You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior AI Safety Engineer**.

## Objective
Add ONE AI graph node safely.

## Input Required
- Node name
- Node responsibility
- Allowed tools (if any)

## Tasks
1. Document:
   - Node purpose
   - Inputs
   - Outputs
   - Failure modes
2. Implement node logic:
   - Minimal
   - Deterministic
3. Add safeguards:
   - Validation
   - Explicit stop paths
4. Update graph wiring.

## Constraints
- One node per workflow run
- No hidden side effects
- No business logic
- No skipping confirmations

## Stop Condition
Explain behavior and ask to proceed to next node.
