---
trigger: always_on
---

# IRIS / Paytime AI Billing System — Pull Request Checklist (ALWAYS)

> This checklist MUST be mentally (and explicitly) passed before any code, refactor,
> or architectural change is considered “done”.

If any item below fails → **STOP, fix, and re-evaluate**.

---

## 1. Architectural Compliance (MANDATORY)

### 1.1 Clean Architecture
- [ ] Domain layer has **zero** imports from:
  - FastAPI
  - SQLAlchemy
  - Celery
  - Redis
  - External APIs
- [ ] Application layer only depends on:
  - Domain
  - Ports (interfaces)
- [ ] Infrastructure implements ports and is injected
- [ ] Interfaces (controllers/webhooks) are thin and contain no business logic
- [ ] Dependency direction always points inward

❌ If any layer violation exists → PR is invalid.

---

## 2. DDD & Business Correctness

### 2.1 Ubiquitous Language
- [ ] Naming matches business language (Boleto, Reminder, Payment, Ledger)
- [ ] No generic names (`Service`, `Manager`, `Helper`) without clear intent
- [ ] Each aggregate has a clear responsibility and invariants

### 2.2 Business Rules
- [ ] All financial rules are explicit and enforced
- [ ] No hidden assumptions
- [ ] No duplicated business logic across layers
- [ ] AI does not own business decisions

❌ If business logic is unclear or duplicated → reject PR.

---

## 3. AI Safety & Behavior Compliance

### 3.1 AI Boundaries
- [ ] LLM is used only for:
  - Intent classification
  - Entity extraction
  - Clarification
  - Tool selection
- [ ] No direct LLM calls inside domain or infrastructure logic
- [ ] All financial actions require deterministic validation

### 3.2 Confirmation & Hallucination Prevention
- [ ] Explicit confirmation required for monetary actions
- [ ] No inferred amounts, dates, rates, or contacts
- [ ] AI never invents IDs or system states

❌ If AI can act without confirmation → critical defect.

---

## 4. File Size & Code Organization

### 4.1 File Limits
- [ ] No file exceeds **300 lines**
- [ ] Files >200 lines reviewed for refactor opportunity
- [ ] Responsibilities are narrow and well-defined

### 4.2 Structure
- [ ] Code organized by bounded context
- [ ] No “utils” dumping grounds
- [ ] No god classes or god modules

---

## 5. Database & Migrations (Alembic)

### 5.1 Schema Changes
- [ ] All DB changes are via Alembic migrations
- [ ] Migrations are reversible (or explicitly documented if not)
- [ ] Constraints, indexes, and FKs are explicit
- [ ] Financial tables include auditability fields where required

### 5.2 Data Safety
- [ ] No destructive migrations without clear rollback plan
- [ ] No manual DB changes outside migrations
- [ ] Idempotency keys are enforced where applicable

---

## 6. External Integrations (Paytime / Messaging)

### 6.1 Provider Abstractions
- [ ] Paytime integration uses a provider interface (port)
- [ ] Messaging uses a `MessagingProvider` abstraction
- [ ] No direct API calls from controllers or domain logic

### 6.2 Reliability
- [ ] External calls have:
  - timeouts
  - retries
  - failure handling
- [ ] Webhooks are idempotent and verified

---

## 7. Async Jobs & Automations (Celery)

### 7.1 Task Safety
- [ ] All tasks are idempotent
- [ ] Tasks are retry-safe
- [ ] Duplicate execution does not corrupt state

### 7.2 Scheduling
- [ ] Reminder schedules respect business rules
- [ ] No hardcoded cron logic inside business code
- [ ] Opt-out and stop conditions are enforced

---

## 8. Messaging & Outbox Pattern

- [ ] Outbound messages are written to DB before sending
- [ ] Message sending is async and retryable
- [ ] Failures are logged and observable
- [ ] No message is sent without a persisted record

❌ If messaging bypasses the outbox → PR rejected.

---

## 9. Security & Compliance

### 9.1 Security
- [ ] No secrets, tokens, or credentials in code or logs
- [ ] Webhooks are verified
- [ ] Sensitive data is not logged
- [ ] Tenant isolation is respected

### 9.2 LGPD / Privacy
- [ ] Data stored is minimal and justified
- [ ] No unnecessary conversation logs
- [ ] Clear data ownership boundaries

---

## 10. Observability & Operations

- [ ] Structured logs include:
  - correlation_id
  - tenant_id
  - entity_id (when applicable)
- [ ] Errors are classified (retryable vs fatal)
- [ ] No silent failures
- [ ] Health checks still pass

---

## 11. Testing & Quality

### 11.1 Tests
- [ ] Domain logic is unit tested
- [ ] Repositories have integration tests
- [ ] External providers have contract or mock tests
- [ ] Critical flows have coverage

### 11.2 Testability
- [ ] Code is easy to test without infrastructure
- [ ] Heavy mocking is not required
- [ ] If testing is painful → architecture must be fixed

---

## 12. Performance & Cost Awareness

- [ ] No unnecessary external calls
- [ ] Messaging volume is controlled
- [ ] Background jobs are batched when possible
- [ ] LLM usage is minimal and justified

---

## 13. Documentation & Clarity

- [ ] Architecture decisions are documented
- [ ] Complex logic is explained with comments or docs
- [ ] Assumptions are explicitly stated
- [ ] README / internal docs updated if needed

---

## 14. Anti-Patterns Check (FINAL GATE)

Confirm NONE of the following exist:
- [ ] Business logic in controllers
- [ ] LLM making financial decisions
- [ ] Direct DB access from AI orchestration
- [ ] Large “god services”
- [ ] Hidden side effects
- [ ] Silent failures
- [ ] Magic numbers or hardcoded policies

If ANY box is checked → PR must be revised.

---

## 15. Final Sign-Off Question (Mandatory)

Before finalizing, answer honestly:

> “Would I confidently deploy this to production in a financial system handling real money and defend it in an audit or incident review?”

- [ ] YES → PR can be finalized
- [ ] NO  → Fix before proceeding

---

## Golden Rule
**Correctness, auditability, and trust are more important than speed.**

Shipping something “almost right” in a financial system is worse than not shipping at all.
