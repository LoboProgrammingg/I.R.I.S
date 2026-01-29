---
trigger: always_on
---

# IRIS / Paytime AI Billing System — Architecture Rules (Windsurf ALWAYS)

> This document defines the **non-negotiable architecture** for the IRIS / Paytime AI Billing System.  
> Any implementation must follow these rules to remain scalable, auditable, and maintainable.

---

## 0. Guiding Principles

### 0.1. Architecture Goals
- **Auditability first** (financial system)
- **Predictability over cleverness**
- **Strict boundaries** (Clean Architecture + DDD)
- **Composable integrations** (Paytime, messaging, LLMs)
- **Cost control** in messaging and infra
- **Idempotency everywhere** (webhooks, tasks, external calls)

### 0.2. Key Non-Goals (MVP)
- Complex analytics dashboards
- Full multi-channel CRM
- Automated legal collections
- Multi-currency support (unless explicitly required)

---

## 1. System Context (What We Are Building)

A WhatsApp-first AI finance assistant that:
- Receives text/audio requests
- Creates **boletos** via **Paytime**
- Sends boletos to contacts
- Runs **daily reminders** until paid
- Applies **interest/penalties** after due date
- Tracks **income/expenses** (ledger)
- Ensures **high reliability and full audit trails**

---

## 2. High-Level Architecture

### 2.1. Primary Components
- **API Service (FastAPI)**: webhooks + user APIs
- **Worker Service (Celery)**: reminders, retries, reconciliation
- **PostgreSQL**: source of truth + auditing
- **Redis**: Celery broker + ephemeral conversation state
- **LLM Orchestrator**: deterministic flows (LangGraph), tool-based actions
- **Messaging Providers**: official WhatsApp + automation sender (swappable)
- **Billing Provider**: Paytime adapter (swappable)

### 2.2. High-Level Diagram (ASCII)

             +---------------------+
             |   WhatsApp Users    |
             +----------+----------+
                        |
                        | inbound msg/audio
                        v
             +----------+----------+
             |   FastAPI Webhook   |
             | (Interfaces Layer)  |
             +----------+----------+
                        |
                        | DTOs / Commands
                        v
             +----------+----------+
             | Application Layer   |
             |  Use Cases / Ports  |
             +----------+----------+
                        |
        +---------------+-------------------+
        |                                   |
        v                                   v

+-----------+-----------+ +----------+----------+
| Domain Layer | | Infrastructure |
| Entities/VO/Services | | DB/Providers/Celery |
+-----------+-----------+ +----------+----------+
| |
| persistence via repos | external calls
v v
+------+-------+ +------+------+
| PostgreSQL | | Paytime |
| Alembic | | API/Webhook |
+------+-------+ +------+------+
|
| outbox / events
v
+------+-------+ +----------------------+
| Celery Worker|------------->| Messaging Provider(s) |
| + Redis | outbound | (WhatsApp/Sender) |
+--------------+ +----------------------+


---

## 3. Clean Architecture Boundaries (Non-Negotiable)

### 3.1. Layers & Dependency Rules
- **Domain**: no imports from FastAPI, SQLAlchemy, Celery, Redis, external clients
- **Application**: depends on Domain; defines **ports** (interfaces)
- **Infrastructure**: implements ports (DB, Paytime client, messaging, LLM tools)
- **Interfaces**: HTTP/webhooks only; maps requests to use cases

**Dependency direction:**

Interfaces -> Application -> Domain
Infrastructure -> Application -> Domain
(never the reverse)


### 3.2. Communication Pattern
- Interfaces create **Commands/Queries** → call Use Cases
- Use Cases call:
  - Domain services (pure logic)
  - Repository ports
  - Provider ports (Paytime/Messaging)
- Infrastructure implements ports and is injected (DI)

---

## 4. Bounded Contexts (DDD)

### 4.1. Bounded Context List
1. **Identity & Tenancy**
2. **Contacts**
3. **Billing (Boletos)**
4. **Collections (Reminders, Delinquency, Interest)**
5. **Finance Ledger (Income/Expenses)**
6. **Messaging**
7. **AI Orchestration**

### 4.2. Context Responsibilities
#### 1) Identity & Tenancy
- Tenants, users, roles (MVP can be minimal)
- Enforces tenant scoping on all data access

#### 2) Contacts
- Stores contact name + phone
- Resolves fuzzy matches with explicit confirmation (if needed)

#### 3) Billing (Boletos)
- Creates/updates boleto state
- Stores Paytime identifiers
- Enforces invariants: amount, due date, payer identity

#### 4) Collections
- Reminder schedules
- Interest/penalty policies
- Stop rules: paid/cancelled/disputed/opt-out

#### 5) Finance Ledger
- Records income/expense transactions
- Links payments to ledger entries

#### 6) Messaging
- Abstracts outbound sends
- Stores delivery attempts
- Supports Outbox pattern

#### 7) AI Orchestration
- Intent classification, entity extraction
- Tool invocation (never business logic)
- Conversation state (ephemeral) + minimal persistence

---

## 5. Domain Model (Core Concepts)

### 5.1. Entities / Aggregates (MVP)
- **Tenant**
- **User**
- **Contact**
- **Boleto** (Aggregate Root)
- **Payment**
- **ReminderSchedule**
- **MessageOutboxItem**
- **LedgerTransaction**

### 5.2. Value Objects (examples)
- Money (amount + currency if needed)
- PhoneNumber (normalized E.164)
- DueDate
- InterestPolicy
- IdempotencyKey

### 5.3. Domain Events (examples)
- `BoletoCreated`
- `BoletoSent`
- `BoletoPaid`
- `BoletoOverdue`
- `InterestApplied`
- `ReminderScheduled`
- `ReminderSent`
- `MessageDeliveryFailed`

Events are persisted (audit trail) or stored in an event table.

---

## 6. Critical Patterns (Must Use)

### 6.1. Idempotency (Every External Trigger)
All these must be idempotent:
- WhatsApp inbound webhook
- Paytime webhooks
- Celery tasks
- Boleto creation calls

**Rule:** every trigger must carry or produce an **idempotency key** and persist it.

### 6.2. Outbox Pattern (Reliable Messaging)
Outbound messages must be written to DB first, then delivered asynchronously.

Flow:
1. Use case writes **MessageOutboxItem** (PENDING)
2. Celery task sends via provider
3. Update outbox item status (SENT/FAILED/RETRYING)

This avoids lost messages and supports retries safely.

### 6.3. Retry & Backoff
- External calls (Paytime/messaging) must have:
  - timeouts
  - retries with exponential backoff
  - circuit breaker (optional but recommended)

### 6.4. “Confirm Before Money Moves”
The system must request explicit confirmation when any ambiguity exists:
- Contact match is uncertain
- Amount is missing or suspicious
- Due date is unclear
- Interest policy not configured

---

## 7. AI Orchestration Architecture (Deterministic)

### 7.1. LLM Responsibilities (Strict)
LLM can:
- classify intent
- extract entities
- propose actions
- ask clarification questions

LLM cannot:
- create a boleto directly
- bypass validation rules
- invent values, rates, or contact data

### 7.2. Graph Flow (LangGraph Recommended)

[Input]
-> (if audio) Transcribe
-> Classify Intent
-> Extract Entities
-> Validate Request (deterministic)
-> If missing/ambiguous: Ask Clarifying Question
-> If ok: Execute Use Case via tools
-> Respond
-> Audit log


### 7.3. Memory Strategy
- Redis: short-term context (conversation state)
- PostgreSQL: long-term minimal data (do not store unnecessary PII)

---

## 8. Interface Design Rules

### 8.1. FastAPI
- Keep controllers thin
- Controllers only:
  - parse/validate request
  - map to use case DTO
  - return response DTO

### 8.2. Webhook Verification
- WhatsApp and Paytime webhooks must be verified:
  - signature validation
  - timestamp/nonce checks if available
- Reject unknown sources

---

## 9. Data & Persistence Rules (PostgreSQL + Alembic)

### 9.1. Schema Rules
- Use strong constraints and indexes
- Enforce tenant scoping at query level (and ideally DB-level policy later)
- Never store secrets in DB
- Store audit/event logs for:
  - boleto lifecycle changes
  - reminder sends
  - payment updates

### 9.2. Alembic Rules
- Every model change requires an Alembic migration
- Migrations must be reversible where possible
- Use explicit names for constraints and indexes

---

## 10. Background Jobs (Celery)

### 10.1. Required Tasks (MVP)
- `deliver_outbox_messages`
- `schedule_reminders_for_due_boletos`
- `send_due_reminders`
- `apply_interest_for_overdue_boletos`
- `reconcile_paytime_status`

### 10.2. Scheduling
- Daily reminders at a configured time window per tenant
- Avoid spam: enforce rate limits + opt-out rules

### 10.3. Safety Rules
- Every task must be idempotent
- Each task must store an execution record (optional but recommended)

---

## 11. Observability & Operations

### 11.1. Structured Logs
All logs must include:
- correlation_id
- tenant_id
- user_id (if available)
- entity_id (boleto_id, message_id, etc.)

### 11.2. Health Checks
- `/health` (basic)
- `/ready` (DB/Redis connectivity)
- optional `/metrics`

### 11.3. Auditability
Any financial action must be auditable:
- Who requested it
- When it happened
- What changed
- External reference IDs (Paytime)

---

## 12. Folder Structure (Canonical)

app/
main.py

config/
settings.py
logging.py

interfaces/
http/
routers/
schemas/
dependencies/
webhooks/
whatsapp.py
paytime.py

application/
dto/
ports/
repositories/
providers/
use_cases/
billing/
contacts/
collections/
finance/

domain/
billing/
contacts/
collections/
finance/
messaging/
shared/

infrastructure/
db/
session.py
models/
repositories/
migrations/ # Alembic
providers/
paytime/
messaging/
llm/
celery/
app.py
tasks/

tests/
unit/
integration/


---

## 13. Implementation Sequence (Must Follow)
1. Architecture docs (this file) + domain glossary
2. Settings + configuration
3. Database session + Alembic init
4. Core tables + migrations (tenant/user/contact)
5. Billing aggregate + repository ports
6. Paytime provider port + stub infra implementation
7. WhatsApp webhook receiver (thin controller)
8. Outbox pattern + Celery worker
9. Reminder scheduling + delinquency rules
10. Payment reconciliation + Paytime webhooks
11. AI graph + tool interfaces
12. Hardening (idempotency, retries, rate limiting, monitoring)

---

## 14. Architectural “Do Not” List
- Do not put SQLAlchemy models in Domain
- Do not call Paytime directly from controllers
- Do not allow LLM to bypass business rules
- Do not create large “utils.py” dumping grounds
- Do not write 1000-line service classes
- Do not implement messaging without an outbox
- Do not skip migrations or create DB manually

---

## 15. Open Questions Placeholder
When rules are missing (interest policy, reminder windows, opt-out logic),
you must:
- stop implementation
- document assumptions
- ask for explicit product decision before proceeding

**Architecture is only correct if business rules are explicit.**