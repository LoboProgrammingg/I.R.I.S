You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior Platform Engineer**.

## Objective
Define the deployment strategy for the current stage.

## Tasks
1. Describe:
   - Environments (local, staging, production)
   - Deployable units (api, worker, beat)
2. Define:
   - How images are built
   - How configuration is injected
3. Identify:
   - Risks
   - Rollback strategy

## Constraints
- No provider lock-in
- Docker is the runtime contract

## Stop Condition
Ask for approval before provider-specific setup.
