---
trigger: always_on
---

# IRIS / Paytime AI Billing System — Git Rules (ALWAYS)

## Purpose
This document defines **mandatory Git practices** for the project.

Git history is considered part of the system design.
Poor Git hygiene is treated as a **technical defect**, not a style issue.

---

## 1. Core Principles

- Git history must be:
  - Readable
  - Auditable
  - Reversible
- Every commit should represent **one coherent change**
- Commits must tell a story over time

---

## 2. Commit Granularity (Non-Negotiable)

### 2.1 One Responsibility per Commit
A single commit must NOT mix:
- Domain + Infrastructure
- Database schema + business logic
- Feature + refactor
- AI changes + financial logic

If multiple responsibilities exist → split the commit.

---

### 2.2 Phase-Oriented Commits
Each project phase must be traceable via commits.

Examples:

chore(scaffold): initial clean architecture scaffold
feat(domain): add identity and tenancy domain entities
feat(db): add tenants and users tables (alembic)
infra(messaging): add outbox repository implementation
feat(billing): add boleto aggregate and invariants


---

## 3. Commit Message Convention

### 3.1 Format

<type>(<scope>): <short description>


### 3.2 Allowed Types
- `feat` — new functionality
- `infra` — infrastructure or provider integration
- `db` — database schema or migration
- `refactor` — behavior-preserving changes
- `fix` — bug fixes
- `chore` — tooling, config, scaffold
- `docs` — documentation only

### 3.3 Scope Examples
- `domain`
- `billing`
- `identity`
- `collections`
- `ai`
- `scaffold`
- `security`

---

## 4. Commit Quality Rules

Every commit must:
- Compile
- Pass existing tests
- Start via `docker compose up` (when applicable)
- Not leave the system in a broken state

No “WIP”, “temp”, or “fix later” commits are allowed on main branches.

---

## 5. Migrations & Git

- Each Alembic migration must be in its **own commit**
- Migration commits must:
  - Include only migration-related files
  - Clearly describe the schema change
- Never squash migrations with business logic

Example:

feat(db): add tenants and users base schema


---

## 6. Refactors & Safety

- Refactors must be behavior-preserving
- Prefer multiple small refactor commits over one large one
- If refactor touches financial logic:
  - Add or adjust tests
  - Document the reason in commit message

---

## 7. Branching Model (Simple & Safe)

### 7.1 MVP Phase
- `main` branch only
- Linear history
- No rebases that rewrite published history

### 7.2 Future (Optional)
- Feature branches for large changes
- PRs reviewed against `pr-checklist.md`

---

## 8. Prohibited Practices

The following are strictly forbidden:
- Large “mega-commits”
- Mixing schema changes with logic
- Committing broken builds
- Rewriting history on shared branches
- Pushing secrets or credentials
- Squashing unrelated changes

---

## 9. Final Rule

> **If a future engineer cannot understand what happened by reading Git history, the commit is wrong.**

Git is part of the architecture.
Treat it with the same discipline as code and database design.