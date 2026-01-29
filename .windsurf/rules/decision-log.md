---
trigger: model_decision
---

# IRIS / Paytime AI Billing System — Architecture Decision Log (ADR)

## Purpose
This document records **all significant architectural and technical decisions** made during the lifecycle of the IRIS / Paytime system.

Its goals are:
- Preserve decision context over time
- Avoid re-discussing solved problems
- Explain *why* something was done, not just *what*
- Support audits, onboarding, and future refactors

Every major decision must be recorded here.

---

## ADR Format (MANDATORY)

Each decision must follow this template:

### ADR-XXX: <Short Title>

**Status:** Proposed | Accepted | Superseded | Deprecated  
**Date:** YYYY-MM-DD  
**Decision Owner:** Team / Tech Lead / Architecture  
**Context:**  
Describe the problem or situation that required a decision.

**Decision:**  
Describe what was decided.

**Rationale:**  
Explain why this option was chosen over alternatives.

**Alternatives Considered:**  
List alternatives and why they were rejected.

**Consequences:**  
Positive and negative consequences of the decision.

**Notes:**  
Any follow-up actions or future review triggers.

---

## ADR-001: Use Clean Architecture with DDD

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
The system handles financial operations, automated billing, and AI-driven workflows. Long-term maintainability, auditability, and correctness are critical.

**Decision:**  
Adopt **Clean Architecture** combined with **Domain-Driven Design (DDD)** as the foundational architectural approach.

**Rationale:**  
- Clear separation of concerns
- Business logic protected from framework churn
- Enables deterministic AI interaction
- Improves testability and auditability

**Alternatives Considered:**  
- MVC monolith → rejected (tight coupling)
- Layered architecture without domain isolation → rejected

**Consequences:**  
- Higher upfront design effort
- Lower long-term maintenance cost

---

## ADR-002: AI as Orchestrator, Not Decision Maker

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
The system uses LLMs to interact with users via natural language, including financial requests.

**Decision:**  
The AI is restricted to:
- Intent classification
- Entity extraction
- Clarification
- Tool selection

All business logic remains deterministic and outside the AI.

**Rationale:**  
- Prevent hallucination
- Enable auditability
- Reduce legal and financial risk

**Alternatives Considered:**  
- AI-driven business logic → rejected (unacceptable risk)

**Consequences:**  
- More tooling and validation layers
- Stronger system guarantees

---

## ADR-003: PostgreSQL + Alembic for Persistence

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
The system requires transactional safety, constraints, and strong consistency.

**Decision:**  
Use **PostgreSQL** as the primary datastore and **Alembic** for all schema migrations.

**Rationale:**  
- Strong ACID guarantees
- Rich constraint support
- Mature tooling

**Alternatives Considered:**  
- NoSQL → rejected (financial data)
- Manual migrations → rejected (audit risk)

**Consequences:**  
- Requires disciplined migration management

---

## ADR-004: Outbox Pattern for Messaging

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
Message delivery (WhatsApp reminders, boleto sending) must be reliable and auditable.

**Decision:**  
Implement the **Outbox Pattern** for all outbound messages.

**Rationale:**  
- Prevent lost messages
- Enable retries and auditing
- Decouple message intent from delivery

**Alternatives Considered:**  
- Direct send from business logic → rejected

**Consequences:**  
- Additional tables and async workers
- Strong delivery guarantees

---

## ADR-005: Celery + Redis for Async Jobs

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
The system requires scheduled reminders, retries, and background reconciliation.

**Decision:**  
Use **Celery** with **Redis** as broker and backend.

**Rationale:**  
- Proven ecosystem
- Supports retries, backoff, scheduling
- Easy horizontal scaling

**Alternatives Considered:**  
- Cron jobs → rejected (non-resilient)
- Cloud-specific queues → postponed

**Consequences:**  
- Requires careful idempotency design

---

## ADR-006: Hybrid WhatsApp Messaging Strategy

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
Official WhatsApp API costs scale with message volume.

**Decision:**  
Adopt a hybrid strategy:
- Official WhatsApp API for user-initiated conversations
- Secondary automation sender for reminders and follow-ups

**Rationale:**  
- Cost optimization
- Flexibility
- Provider abstraction allows future replacement

**Alternatives Considered:**  
- Official API only → rejected (cost)
- Unofficial only → rejected (risk)

**Consequences:**  
- Increased complexity
- Requires strict provider abstraction

---

## ADR-007: Deterministic AI Graph (LangGraph)

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
AI flows must be predictable and safe.

**Decision:**  
Use a **graph-based orchestration model** (LangGraph or equivalent).

**Rationale:**  
- Enforces step order
- Prevents skipped validations
- Enables inspection and debugging

**Alternatives Considered:**  
- Free-form LLM prompts → rejected

**Consequences:**  
- More upfront modeling
- Much safer AI behavior

---

## ADR-008: Explicit Confirmation for Financial Actions

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
Users interact via natural language, which is inherently ambiguous.

**Decision:**  
Require **explicit user confirmation** before any monetary action.

**Rationale:**  
- Prevents accidental charges
- Legal and compliance safety
- Improves user trust

**Alternatives Considered:**  
- Implicit confirmation → rejected

**Consequences:**  
- Slightly slower user flow
- Much lower risk

---

## ADR-009: Tenant-First Data Isolation

**Status:** Accepted  
**Date:** 2026-01-XX  

**Context:**  
The system is a SaaS with potential B2C and B2B usage.

**Decision:**  
All data models and queries are scoped by `tenant_id`.

**Rationale:**  
- Prevent data leakage
- Enable future multi-tenant scaling

**Alternatives Considered:**  
- Single-tenant design → rejected

**Consequences:**  
- Additional query constraints
- Strong isolation guarantees

---

## Review & Evolution Rules

- New ADRs must be added for:
  - Architectural changes
  - New core technologies
  - Security model changes
- Superseded ADRs must remain for historical context
- ADRs are immutable once Accepted (only superseded)

## ADR-010: Apply Interest via Scheduled Background Job

**Status:** Accepted  
**Date:** 2026-01-29  

**Context:**  
Interest and penalties must be applied consistently and safely for overdue boletos.

**Decision:**  
Interest and penalties will be applied exclusively via a scheduled background job
(Celery), executed daily.

**Rationale:**  
- Avoids real-time calculation errors
- Ensures deterministic and auditable behavior
- Simplifies AI responsibilities
- Prevents repeated interest application

**Alternatives Considered:**  
- Apply interest on every boleto read → rejected (non-deterministic)
- Apply interest via AI logic → rejected (unsafe)

**Consequences:**  
- Requires daily scheduled task
- Interest application becomes auditable via domain events


---

## Final Principle

> **Architecture decisions outlive code.  
> Code can be rewritten. Decisions must be remembered.**
