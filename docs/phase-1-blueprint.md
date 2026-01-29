# IRIS / Paytime AI Billing System — Phase 1: Project Blueprint

**Version:** 1.0  
**Date:** 2026-01-29  
**Status:** Draft — Awaiting Approval

---

## 1. Executive Summary

IRIS is a **WhatsApp-first AI finance assistant** that:
- Receives text/audio requests from users
- Creates **boletos** (Brazilian payment slips) via **Paytime**
- Sends boletos to contacts
- Runs **automated daily reminders** until paid
- Applies **interest/penalties** after due date
- Tracks **income/expenses** (simple ledger)
- Ensures **high reliability, full audit trails, and financial safety**

This is a **production-grade, multi-tenant SaaS** designed for long-term maintainability.

---

## 2. Architecture Overview

### 2.1 Architectural Style

**Clean Architecture + Domain-Driven Design (DDD)**

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACES LAYER                         │
│  (FastAPI Controllers, Webhooks, Request/Response Schemas)  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│    (Use Cases, DTOs, Ports/Interfaces, Orchestration)        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                             │
│  (Entities, Value Objects, Domain Services, Domain Events)   │
│                  NO EXTERNAL DEPENDENCIES                    │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│   (PostgreSQL, Redis, Paytime Client, Messaging Providers,   │
│    Celery Workers, LLM Clients, Repository Implementations)  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Dependency Rules (Non-Negotiable)

- **Domain** → No imports from FastAPI, SQLAlchemy, Celery, Redis, external clients
- **Application** → Depends on Domain; defines **ports** (interfaces)
- **Infrastructure** → Implements ports; injected via DI
- **Interfaces** → HTTP/webhooks only; maps requests to use cases

**Dependencies always point inward.**

### 2.3 High-Level Component Diagram

```
         ┌─────────────────┐
         │  WhatsApp Users │
         └────────┬────────┘
                  │ inbound msg/audio
                  ▼
         ┌────────────────────┐
         │  FastAPI Webhook   │
         │ (Interfaces Layer) │
         └────────┬───────────┘
                  │ Commands / DTOs
                  ▼
         ┌────────────────────┐
         │ Application Layer  │
         │  Use Cases / Ports │
         └────────┬───────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌───────────────┐    ┌─────────────────┐
│ Domain Layer  │    │ Infrastructure  │
│ Pure Logic    │    │ DB/Providers    │
└───────────────┘    └────────┬────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌───────────┐   ┌───────────┐   ┌─────────────┐
       │ PostgreSQL│   │  Paytime  │   │  Messaging  │
       │ + Alembic │   │    API    │   │  Providers  │
       └───────────┘   └───────────┘   └─────────────┘
                              
         ┌─────────────────────────────┐
         │     Celery + Redis          │
         │  (Reminders, Reconciliation)│
         └─────────────────────────────┘
```

---

## 3. Bounded Contexts

### 3.1 Context Map

| Context | Responsibility | Key Aggregates |
|---------|----------------|----------------|
| **Identity & Tenancy** | Tenant/user management, authentication, authorization | Tenant, User |
| **Contacts** | Contact registry, fuzzy matching, phone normalization | Contact |
| **Billing** | Boleto lifecycle, Paytime integration | Boleto, Payment |
| **Collections** | Reminders, delinquency, interest/penalties | ReminderSchedule, InterestPolicy |
| **Finance Ledger** | Income/expense tracking | LedgerTransaction |
| **Messaging** | Outbound message abstraction, delivery tracking | MessageOutboxItem |
| **AI Orchestration** | Intent classification, entity extraction, tool invocation | ConversationState |

### 3.2 Context Relationships

```
┌──────────────────┐     ┌──────────────────┐
│ Identity/Tenancy │────▶│     Contacts     │
└──────────────────┘     └────────┬─────────┘
         │                        │
         │                        ▼
         │               ┌──────────────────┐
         └──────────────▶│     Billing      │◀────────┐
                         └────────┬─────────┘         │
                                  │                   │
                    ┌─────────────┼─────────────┐     │
                    ▼             ▼             ▼     │
          ┌──────────────┐ ┌────────────┐ ┌──────────┴───┐
          │ Collections  │ │  Ledger    │ │  Messaging   │
          └──────────────┘ └────────────┘ └──────────────┘
                    ▲             ▲             ▲
                    └─────────────┼─────────────┘
                                  │
                         ┌────────┴────────┐
                         │ AI Orchestration│
                         │   (reads only)  │
                         └─────────────────┘
```

---

## 4. Core Domain Concepts

### 4.1 Entities & Aggregates

| Entity | Type | Description |
|--------|------|-------------|
| **Tenant** | Aggregate Root | Logical customer account; all data scoped by tenant |
| **User** | Entity | Human operator; initiates actions via WhatsApp/UI |
| **Contact** | Aggregate Root | Person/entity that receives boletos |
| **Boleto** | Aggregate Root | Payment request instrument via Paytime |
| **Payment** | Entity | Confirmed monetary settlement of a boleto |
| **ReminderSchedule** | Entity | Scheduled reminder for a boleto |
| **MessageOutboxItem** | Entity | Persisted outbound message for reliable delivery |
| **LedgerTransaction** | Aggregate Root | Financial entry (income/expense) |
| **InterestPolicy** | Value Object | Configuration for penalties/interest |

### 4.2 Value Objects

| Value Object | Description |
|--------------|-------------|
| **Money** | Amount + currency (BRL default) |
| **PhoneNumber** | Normalized E.164 format |
| **DueDate** | Validated date with business rules |
| **IdempotencyKey** | Unique key for duplicate prevention |

### 4.3 Domain Events

| Event | Trigger |
|-------|---------|
| `BoletoCreated` | New boleto registered |
| `BoletoSent` | Boleto delivered to contact |
| `BoletoPaid` | Payment confirmed |
| `BoletoOverdue` | Due date passed without payment |
| `BoletoCancelled` | Boleto manually cancelled |
| `InterestApplied` | Penalty/interest added to boleto |
| `ReminderScheduled` | Reminder created |
| `ReminderSent` | Reminder delivered |
| `MessageDeliveryFailed` | Outbound message failed |

### 4.4 Key Invariants

1. **Boleto immutability after PAID** — Cannot modify a paid boleto
2. **No boleto without valid payer** — Contact must exist and be confirmed
3. **Explicit confirmation required** — All monetary actions need user approval
4. **Tenant isolation** — No cross-tenant data access ever
5. **Interest policy must be configured** — Never inferred by AI
6. **Single payment per boleto (MVP constraint)**  
   - Each boleto may be settled by exactly one payment.
   - Partial payments, installments, or split settlements are explicitly NOT supported in the MVP.
   - Any future change requires domain redesign and a new ADR.


---

## 5. High-Level Data Model

### 5.1 Core Tables

```
┌─────────────────────────────────────────────────────────────┐
│                         tenants                              │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ name (VARCHAR)                                              │
│ created_at (TIMESTAMP)                                      │
│ updated_at (TIMESTAMP)                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                          users                               │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ tenant_id (UUID, FK → tenants) [INDEXED]                    │
│ phone_number (VARCHAR, UNIQUE per tenant)                   │
│ name (VARCHAR)                                              │
│ role (ENUM: admin, user)                                    │
│ created_at, updated_at                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        contacts                              │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ tenant_id (UUID, FK → tenants) [INDEXED]                    │
│ name (VARCHAR)                                              │
│ phone_number (VARCHAR, E.164)                               │
│ opt_out (BOOLEAN, default false)                            │
│ created_at, updated_at                                      │
│ UNIQUE(tenant_id, phone_number)                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         boletos                              │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ tenant_id (UUID, FK → tenants) [INDEXED]                    │
│ contact_id (UUID, FK → contacts)                            │
│ created_by_user_id (UUID, FK → users)                       │
│ amount_cents (BIGINT, NOT NULL)                             │
│ due_date (DATE, NOT NULL)                                   │
│ status (ENUM: created, sent, paid, overdue, cancelled, failed)│
│ paytime_boleto_id (VARCHAR, external reference)             │
│ paytime_barcode (VARCHAR)                                   │
│ paytime_pix_code (VARCHAR)                                  │
│ idempotency_key (VARCHAR, UNIQUE)                           │
│ created_at, updated_at                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        payments                              │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ boleto_id (UUID, FK → boletos)                              │
│ amount_cents (BIGINT)                                       │
│ paid_at (TIMESTAMP)                                         │
│ paytime_payment_id (VARCHAR)                                │
│ idempotency_key (VARCHAR, UNIQUE)                           │
│ created_at                                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   reminder_schedules                         │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ boleto_id (UUID, FK → boletos) [INDEXED]                    │
│ scheduled_at (TIMESTAMP)                                    │
│ status (ENUM: scheduled, sent, failed, cancelled)           │
│ attempt_count (INT, default 0)                              │
│ created_at, updated_at                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   message_outbox                             │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ tenant_id (UUID, FK → tenants) [INDEXED]                    │
│ recipient_phone (VARCHAR)                                   │
│ message_type (ENUM: boleto_send, reminder, notification)    │
│ payload (JSONB)                                             │
│ status (ENUM: pending, sent, failed, retrying)              │
│ attempt_count (INT, default 0)                              │
│ last_error (TEXT, nullable)                                 │
│ idempotency_key (VARCHAR, UNIQUE)                           │
│ created_at, updated_at, sent_at                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  ledger_transactions                         │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ tenant_id (UUID, FK → tenants) [INDEXED]                    │
│ type (ENUM: income, expense)                                │
│ amount_cents (BIGINT)                                       │
│ description (VARCHAR)                                       │
│ reference_id (UUID, nullable) — links to boleto/payment     │
│ reference_type (VARCHAR, nullable)                          │
│ recorded_at (TIMESTAMP)                                     │
│ created_at                                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   interest_policies                          │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ tenant_id (UUID, FK → tenants) [UNIQUE]                     │
│ grace_period_days (INT, default 0)                          │
│ daily_interest_rate (DECIMAL)                               │
│ fixed_penalty_cents (BIGINT, default 0)                     │
│ created_at, updated_at                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     audit_events                             │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ tenant_id (UUID) [INDEXED]                                  │
│ entity_type (VARCHAR)                                       │
│ entity_id (UUID)                                            │
│ event_type (VARCHAR)                                        │
│ actor_id (UUID, nullable)                                   │
│ payload (JSONB)                                             │
│ created_at                                                  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Key Constraints & Indexes

- All tables have `tenant_id` indexed for query scoping
- `boletos.idempotency_key` UNIQUE — prevents duplicate creation
- `message_outbox.idempotency_key` UNIQUE — prevents duplicate sends
- `payments.idempotency_key` UNIQUE — prevents duplicate recording
- Foreign keys enforce referential integrity
- Soft deletes NOT used (MVP) — consider for future

---

## 6. AI Orchestration Approach

### 6.1 Core Principle

**AI is an orchestrator, NOT a decision maker.**

The LLM:
- Classifies intent
- Extracts entities
- Asks clarification questions
- Selects validated tools

The LLM does NOT:
- Execute business logic
- Access database directly
- Invent values (amounts, dates, rates)
- Bypass confirmation requirements

### 6.2 Graph-Based Execution (LangGraph)

```
┌─────────────┐
│   INPUT     │ (text or audio)
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Transcribe Audio │ (if needed)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Classify Intent  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Extract Entities │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Validate Request │ (deterministic)
└──────┬───────────┘
       │
       ├──────── Missing? ──────▶ Ask Clarification
       │                                │
       │                                ▼
       │                         ┌────────────┐
       │                         │ Wait Input │
       │                         └──────┬─────┘
       │                                │
       ◀────────────────────────────────┘
       │
       ▼
┌──────────────────────┐
│ Confirmation Required│
└──────┬───────────────┘
       │
       ├──────── Yes ──────▶ Request Confirmation
       │                            │
       │                            ▼
       │                     ┌────────────┐
       │                     │ Wait Input │
       │                     └──────┬─────┘
       │                            │
       ◀────────────────────────────┘
       │
       ▼
┌──────────────────┐
│  Execute Tool    │ (validated, deterministic)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Format Response  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│   Audit Log      │
└──────────────────┘
```

### 6.3 Allowed Intent Categories (MVP)

| Intent | Description |
|--------|-------------|
| `CREATE_BOLETO` | Create a new boleto |
| `SEND_BOLETO` | Send existing boleto to contact |
| `CHECK_BOLETO_STATUS` | Query boleto status |
| `LIST_BOLETOS` | List boletos with filters |
| `CANCEL_BOLETO` | Cancel an existing boleto |
| `CONFIGURE_INTEREST` | Set interest/penalty policy |
| `CONFIGURE_REMINDERS` | Set reminder preferences |
| `REGISTER_CONTACT` | Add new contact |
| `LIST_CONTACTS` | Query contacts |
| `RECORD_EXPENSE` | Manual expense entry |
| `RECORD_INCOME` | Manual income entry |
| `FINANCIAL_SUMMARY` | View ledger summary |
| `GENERAL_QUESTION` | Non-financial query |
| `UNKNOWN` | Cannot classify → ask clarification |

### 6.4 Tools (System Actions)

Each tool is a validated, deterministic operation:

| Tool | Domain | Requires Confirmation |
|------|--------|----------------------|
| `create_boleto` | Billing | Yes |
| `send_boleto` | Messaging | Yes |
| `cancel_boleto` | Billing | Yes |
| `get_boleto_status` | Billing | No |
| `list_boletos` | Billing | No |
| `register_contact` | Contacts | No |
| `lookup_contact` | Contacts | No |
| `record_expense` | Ledger | Yes |
| `record_income` | Ledger | Yes |
| `get_financial_summary` | Ledger | No |
| `set_interest_policy` | Collections | Yes |

### 6.5 Memory Strategy

| Type | Storage | TTL | Purpose |
|------|---------|-----|---------|
| Conversation State | Redis | 30 min | Flow continuity |
| Pending Confirmations | Redis | 5 min | Confirmation tracking |
| Audit Logs | PostgreSQL | Permanent | Compliance |

---

## 7. Async Jobs Overview (Celery)

### 7.1 Required Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `deliver_outbox_messages` | Every 1 min | Process pending messages |
| `schedule_reminders_for_due_boletos` | Daily 8:00 AM | Create reminder schedules |
| `send_due_reminders` | Every 5 min | Send scheduled reminders |
| `apply_interest_for_overdue_boletos` | Daily 00:00 | Apply interest/penalties |
| `reconcile_paytime_status` | Every 15 min | Sync boleto status from Paytime |
| `cleanup_expired_conversations` | Daily 03:00 | Remove stale Redis state |

### 7.2 Task Safety Rules

1. **Idempotency** — Every task must be safe to run multiple times
2. **Retry with backoff** — Exponential backoff for failures
3. **Dead letter handling** — Log and alert on permanent failures
4. **Rate limiting** — Respect messaging quotas

---

## 8. External Integrations

### 8.1 Paytime (Billing Provider)

| Operation | Direction | Idempotency |
|-----------|-----------|-------------|
| Create Boleto | Outbound | Via idempotency_key |
| Cancel Boleto | Outbound | Via boleto_id |
| Get Boleto Status | Outbound | N/A (read) |
| Payment Webhook | Inbound | Via event_id |
| Status Change Webhook | Inbound | Via event_id |

**Provider abstraction required** — `PaytimeProviderPort` interface.

### 8.2 Messaging (WhatsApp)

| Channel | Use Case | Cost Model |
|---------|----------|------------|
| Official WhatsApp API | User-initiated conversations | Per-conversation |
| Automation Sender | Reminders, notifications | Lower cost |

**Provider abstraction required** — `MessagingProviderPort` interface.

### 8.3 LLM (AI)

| Provider | Use Case |
|----------|----------|
| OpenAI / Claude | Intent classification, entity extraction |
| Whisper | Audio transcription |

**Provider abstraction required** — `LLMProviderPort`, `TranscriptionProviderPort`.

---

## 9. Security & Idempotency

### 9.1 Security Measures

| Area | Measure |
|------|---------|
| **Webhook Verification** | HMAC signature validation |
| **Tenant Isolation** | All queries scoped by tenant_id |
| **Secrets** | Environment variables only, never in code |
| **PII Protection** | Masked in logs (+55******1234) |
| **Rate Limiting** | Per-tenant message quotas |
| **Input Validation** | Strict schema validation at interfaces |

### 9.2 Idempotency Points

| Operation | Key Source | Storage |
|-----------|------------|---------|
| Boleto Creation | Client-provided or generated UUID | `boletos.idempotency_key` |
| Message Sending | Generated per message intent | `message_outbox.idempotency_key` |
| Payment Recording | Paytime event_id | `payments.idempotency_key` |
| Webhook Processing | Event ID from provider | Redis (short-term) + DB check |

### 9.3 Confirmation Protocol

All monetary actions require explicit confirmation:

```
AI: "I will create a boleto of R$ 1.200,00 for João Silva, 
     due on 2026-02-15, and send to +55 11 9XXXX-XXXX. 
     Should I proceed?"

User: "Yes" / "Sim" / "Confirma"

→ Only then: Execute tool
```

---

## 10. Observability

### 10.1 Structured Logging

Every log entry includes:
- `correlation_id`
- `tenant_id`
- `user_id` (when applicable)
- `entity_id` (boleto_id, message_id, etc.)

### 10.2 Health Checks

| Endpoint | Purpose |
|----------|---------|
| `/health` | Basic liveness |
| `/ready` | DB + Redis connectivity |

### 10.3 Alerting Triggers (Future)

- Repeated webhook validation failures
- High message failure rate
- Celery task queue backlog
- Paytime API errors

---

## 11. Implementation Roadmap

### Phase 1: Project Blueprint ✅ (Current)
- Architecture documentation
- Domain glossary
- ADRs
- This blueprint

### Phase 2: Repository Scaffold
- `pyproject.toml` + dependencies
- Folder structure (Clean Architecture)
- Docker + docker-compose
- Basic configuration loading
- README

### Phase 3: Database Foundation
- Alembic setup
- Core migrations (tenants, users, contacts)
- Session management
- Repository ports + implementations

### Phase 4: Billing Core
- Boleto entity + repository
- Paytime provider port + stub implementation
- Create/cancel boleto use cases
- Unit tests for domain

### Phase 5: Messaging Infrastructure
- Message outbox table + repository
- Messaging provider port + stub
- Celery setup + outbox delivery task
- Integration tests

### Phase 6: WhatsApp Webhook
- Inbound webhook receiver
- Signature verification
- Basic message routing

### Phase 7: AI Orchestration (MVP)
- LangGraph skeleton
- Intent classification node
- Entity extraction node
- Confirmation gate
- Tool execution nodes
- Integration with use cases

### Phase 8: Collections & Reminders
- Reminder schedule entity
- Daily reminder scheduling task
- Interest policy configuration
- Overdue detection + interest application

### Phase 9: Paytime Integration
- Real Paytime client implementation
- Paytime webhooks (payment, status)
- Payment reconciliation task

### Phase 10: Hardening
- Full idempotency coverage
- Rate limiting
- Error handling polish
- Observability (logs, metrics)
- Security audit

### Phase 11: Production Readiness
- Load testing
- Documentation finalization
- Deployment configuration
- Monitoring setup

---

## 12. Open Questions & Assumptions

### 12.1 Open Questions (Require Product Decision)

| # | Question | Impact |
|---|----------|--------|
| 1 | What is the default reminder schedule? (e.g., daily, 3 days before due, etc.) | Collections logic |
| 2 | What are the default interest/penalty rates if not configured? | InterestPolicy defaults |
| 3 | How many reminder messages per day per contact are allowed? | Rate limiting |
| 4 | Should users be able to configure reminder time windows? (e.g., 9AM-6PM only) | Scheduling complexity |
| 5 | What happens to reminders when a boleto is partially paid? | Partial payment handling |
| 6 | Is audio message response required (TTS)? | AI response channel |
| 7 | What is the opt-out mechanism for contacts? (reply STOP?) | Compliance |
| 8 | Multi-user per tenant: what are the permission levels? | Authorization model |

### 12.2 Assumptions (Proceeding Unless Corrected)

| # | Assumption |
|---|------------|
| 1 | Single currency: BRL (Brazilian Real) |
| 2 | One boleto = one payment (no partial payments MVP) |
| 3 | Tenants are pre-registered (no self-signup MVP) |
| 4 | Interest policy is per-tenant, not per-boleto |
| 5 | Reminders stop immediately on PAID or CANCELLED |
| 6 | All timestamps in UTC, display conversion client-side |
| 7 | Paytime is the only billing provider (abstracted for future) |
| 8 | WhatsApp is the only messaging channel (abstracted for future) |
| 9 | Audio transcription uses Whisper API |
| 10 | LLM responses are text-only (no audio/TTS MVP) |
| 11 | Partial or split payments are explicitly NOT supported in the MVP |

---

## 13. Folder Structure (Target)

```
app/
├── main.py
├── config/
│   ├── settings.py
│   └── logging.py
├── interfaces/
│   ├── http/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── dependencies/
│   └── webhooks/
│       ├── whatsapp.py
│       └── paytime.py
├── application/
│   ├── dto/
│   ├── ports/
│   │   ├── repositories/
│   │   └── providers/
│   └── use_cases/
│       ├── billing/
│       ├── contacts/
│       ├── collections/
│       └── finance/
├── domain/
│   ├── billing/
│   ├── contacts/
│   ├── collections/
│   ├── finance/
│   ├── messaging/
│   └── shared/
├── infrastructure/
│   ├── db/
│   │   ├── session.py
│   │   ├── models/
│   │   └── repositories/
│   ├── migrations/  # Alembic
│   ├── providers/
│   │   ├── paytime/
│   │   ├── messaging/
│   │   └── llm/
│   └── celery/
│       ├── app.py
│       └── tasks/
└── tests/
    ├── unit/
    └── integration/
```

---

## 14. Summary

This blueprint establishes:

- **Clean Architecture + DDD** foundation
- **7 bounded contexts** with clear responsibilities
- **Deterministic AI orchestration** via LangGraph
- **Outbox pattern** for reliable messaging
- **Celery workers** for async jobs
- **Strong idempotency** at all external boundaries
- **Tenant-first isolation** for multi-tenancy
- **Explicit confirmation** for all financial actions

---

**Phase 1 complete. Should I proceed to Phase 2 (repository scaffold)?**
