# IRIS / Paytime AI Billing System — Project Checkpoint

**Checkpoint Date:** 2026-01-29  
**Status:** Development Paused  
**Last Active Phase:** AI Graph Production-Ready Implementation

---

## 1. Project Overview

### What is IRIS?

IRIS is an AI-powered billing assistant that enables users to create, send, and manage **boletos** (Brazilian payment slips) through natural language interactions. The system is designed for WhatsApp-first communication, with automated reminders and payment tracking.

### Core Business Goal

Provide a conversational interface for small business owners to:
- Generate boletos for customers
- Send payment requests via messaging
- Automate payment reminders
- Track payments and manage delinquency
- Record income and expenses

### Target Users

- Small business owners in Brazil
- Service providers who bill clients regularly
- Users who prefer conversational interfaces over traditional dashboards

### Key Constraints

| Constraint | Rationale |
|------------|-----------|
| **Financial Safety** | Every monetary action requires explicit user confirmation |
| **Tenant Isolation** | All data is scoped by `tenant_id` — no cross-tenant access |
| **AI as Orchestrator** | AI classifies intent and extracts entities but never executes business logic |
| **Auditability** | All financial operations must be traceable and logged |
| **Idempotency** | Webhooks, tasks, and external calls must be safely repeatable |
| **Determinism** | AI responses must be predictable and explainable |

---

## 2. Architectural Principles (Locked Decisions)

The following decisions are **final and must not be re-discussed**. They are documented in `.windsurf/rules/decision-log.md`.

### Accepted ADRs

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Clean Architecture + DDD | Accepted |
| ADR-002 | AI as Orchestrator, Not Decision Maker | Accepted |
| ADR-003 | PostgreSQL + Alembic for Persistence | Accepted |
| ADR-004 | Outbox Pattern for Messaging | Accepted |
| ADR-005 | Celery + Redis for Async Jobs | Accepted |
| ADR-006 | Hybrid WhatsApp Messaging Strategy | Accepted |
| ADR-007 | Deterministic AI Graph (LangGraph-style) | Accepted |
| ADR-008 | Explicit Confirmation for Financial Actions | Accepted |
| ADR-009 | Tenant-First Data Isolation | Accepted |
| ADR-010 | Apply Interest via Scheduled Background Job | Accepted |

### Non-Negotiable Rules

1. **Domain layer has zero framework imports** — no FastAPI, SQLAlchemy, Celery, or Redis in domain code
2. **AI never writes to database directly** — all persistence goes through use cases
3. **No monetary action without confirmation** — validation gate + confirmation gate are mandatory
4. **All external calls are idempotent** — webhooks, Celery tasks, provider calls
5. **Tenant isolation at query level** — every query must include `tenant_id`

---

## 3. Implemented Bounded Contexts

### Status Matrix

| Context | Domain | Persistence | Use Cases | HTTP | Jobs | Notes |
|---------|--------|-------------|-----------|------|------|-------|
| **Identity & Tenancy** | ✅ | ✅ | ✅ | ✅ | — | Tenant + User CRUD complete |
| **Contacts** | ✅ | ✅ | ✅ | ✅ | — | Contact CRUD complete |
| **Billing** | ✅ | ✅ | ✅ | ✅ | ✅ | Boleto + Payment lifecycle complete |
| **Messaging (Outbox)** | ✅ | ✅ | ✅ | ✅ | ✅ | Outbox pattern implemented |
| **Collections** | ✅ | ✅ | ⚠️ | — | ⚠️ | Schema ready, use cases partial |
| **AI Orchestration** | ✅ | ✅ (Redis) | ✅ | ✅ | — | Graph + HTTP endpoints complete |

### Context Details

#### Identity & Tenancy
- **Complete:** Tenant entity, User entity, CRUD operations, HTTP endpoints
- **Not implemented:** OAuth, role-based permissions, API keys

#### Contacts
- **Complete:** Contact entity, CRUD operations, phone normalization, HTTP endpoints
- **Not implemented:** Fuzzy matching, duplicate detection

#### Billing
- **Complete:** Boleto aggregate, Payment entity, create/cancel/status use cases, Paytime integration, payment webhook processing, reconciliation task
- **Not implemented:** Bulk operations, PDF generation

#### Messaging (Outbox)
- **Complete:** MessageOutboxItem entity, queue/process use cases, delivery task, HTTP endpoints
- **Not implemented:** Real messaging provider (stub only), retry with backoff

#### Collections
- **Complete:** ReminderSchedule entity, InterestPolicy entity, domain models, database schema
- **Not implemented:** Reminder scheduling use case, interest application use case, reminder sending task

#### AI Orchestration
- **Complete:** Graph structure, all nodes, validation gates, confirmation gates, tools, Redis state, HTTP endpoints, Gemini LLM integration
- **Not implemented:** Audio transcription, multi-turn context beyond TTL, WhatsApp webhook

---

## 4. Database & Migrations Summary

### Applied Migrations

| Migration | Description |
|-----------|-------------|
| `001_add_tenants_and_users.py` | Base identity tables |
| `002_fix_users_fk_to_restrict.py` | Changed FK from CASCADE to RESTRICT |
| `003_add_contacts_table.py` | Contacts table |
| `004_add_boletos_and_payments.py` | Billing tables |
| `005_rename_external_to_provider_reference.py` | Renamed `external_id` → `provider_reference` |
| `006_add_message_outbox.py` | Messaging outbox table |
| `007_add_collections_tables.py` | Reminder schedules + interest policies |

### Tables

| Table | Bounded Context |
|-------|-----------------|
| `tenants` | Identity |
| `users` | Identity |
| `contacts` | Contacts |
| `boletos` | Billing |
| `payments` | Billing |
| `message_outbox` | Messaging |
| `reminder_schedules` | Collections |
| `interest_policies` | Collections |

### Critical Constraints

| Constraint | Table | Behavior |
|------------|-------|----------|
| `users.tenant_id → tenants.id` | users | ON DELETE RESTRICT |
| `contacts.tenant_id → tenants.id` | contacts | ON DELETE RESTRICT |
| `boletos.tenant_id → tenants.id` | boletos | ON DELETE RESTRICT |
| `boletos.contact_id → contacts.id` | boletos | ON DELETE RESTRICT |
| `payments.boleto_id → boletos.id` | payments | ON DELETE RESTRICT |

**Important:** All FK behaviors use RESTRICT to prevent accidental cascade deletions in a financial system.

### Idempotency Guarantees

- `payments.idempotency_key` — unique constraint for webhook deduplication
- `boletos.provider_reference` — unique identifier from Paytime
- `message_outbox.id` — UUID for delivery deduplication

---

## 5. AI Orchestration — Current State

### Graph Structure

The AI graph executes nodes in **strict sequential order**:

```
1. Input Normalization
2. Intent Classification (LLM)
3. Entity Extraction (LLM)
4. Validation Gate (deterministic)
5. Confirmation Gate (deterministic)
6. Tool Execution (use case call)
7. Response Generation (deterministic)
```

### Node Responsibilities

| Node | Responsibility | LLM? |
|------|----------------|------|
| `normalize_input` | Clean and standardize user text | No |
| `classify_intent` | Determine user intent | Yes |
| `extract_entities` | Pull structured data from text | Yes |
| `validate_request` | Check required entities present | No |
| `check_confirmation` | Request/process user confirmation | No |
| `execute_tool` | Dispatch to appropriate use case | No |
| `generate_response` | Format human-readable response | No |

### Supported Intents

- CREATE_BOLETO
- CANCEL_BOLETO
- CHECK_BOLETO_STATUS
- SEND_BOLETO
- LIST_BOLETOS
- GENERAL_QUESTION
- UNKNOWN

### Available Tools

| Tool | Use Case | Requires Confirmation |
|------|----------|----------------------|
| `CreateBoletoTool` | CreateBoletoUseCase | Yes |
| `CancelBoletoTool` | CancelBoletoUseCase | Yes |
| `GetBoletoStatusTool` | GetBoletoStatusUseCase | No |
| `QueueMessageTool` | QueueMessageUseCase | No |

### What the AI CAN Do

- Classify user intent from natural language
- Extract entities (contact, amount, due date, boleto ID)
- Ask clarifying questions when data is missing
- Request explicit confirmation before monetary actions
- Call validated tools to execute use cases
- Generate human-readable responses

### What the AI is FORBIDDEN to Do

- Execute business logic directly
- Write to database
- Call external providers (Paytime, messaging)
- Invent or guess monetary values
- Invent or guess dates or contact information
- Skip validation or confirmation gates
- Proceed without explicit confirmation for financial actions

### Redis Usage

| Key Pattern | Purpose | TTL |
|-------------|---------|-----|
| `ai:state:{conversation_id}` | Conversation state | 30 minutes |
| `ai:confirm:{conversation_id}` | Pending confirmation | 5 minutes |

### Confirmation Expiration

- User has **5 minutes** to confirm pending actions
- After expiration, user must restart the request
- Expired confirmations return HTTP 410 Gone

---

## 6. Runtime Capabilities

### Live Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Basic health check |
| `/ready` | GET | Readiness (DB + Redis) |
| `/tenants` | CRUD | Tenant management |
| `/contacts` | CRUD | Contact management |
| `/boletos` | CRUD | Boleto management |
| `/outbox` | GET/POST | Message queue management |
| `/webhooks/paytime` | POST | Payment webhook receiver |
| `/ai/message` | POST | AI message processing |
| `/ai/confirm` | POST | AI confirmation handling |

### AI Interaction Flow

**New Conversation:**
```
POST /ai/message
{
  "tenant_id": "uuid",
  "text": "Crie um boleto de R$ 500 para João"
}

Response:
{
  "conversation_id": "uuid",
  "response": "Vou criar um boleto de R$ 500,00 para João. Qual a data de vencimento?",
  "requires_confirmation": false,
  "intent": "CREATE_BOLETO"
}
```

**With Confirmation:**
```
POST /ai/message
{
  "conversation_id": "uuid",
  "tenant_id": "uuid",
  "text": "Vencimento dia 15/02"
}

Response:
{
  "conversation_id": "uuid",
  "response": "Vou criar um boleto de R$ 500,00 para João, vencimento 15/02/2026. Confirma?",
  "requires_confirmation": true,
  "intent": "CREATE_BOLETO"
}
```

**Confirmation:**
```
POST /ai/confirm
{
  "conversation_id": "uuid",
  "tenant_id": "uuid",
  "confirmed": true
}

Response:
{
  "conversation_id": "uuid",
  "response": "Boleto criado com sucesso!",
  "action_executed": true,
  "result": { "boleto_id": "uuid", ... }
}
```

### What Uses Stubs vs Real Providers

| Component | Status |
|-----------|--------|
| Paytime Provider | Real client implemented, needs API key |
| Messaging Provider | Stub only (logs instead of sending) |
| Gemini LLM | Real client implemented, needs API key |

---

## 7. External Integrations — Status

### Paytime

| Component | Status |
|-----------|--------|
| PaytimeProviderPort | ✅ Defined |
| PaytimeClient (real) | ✅ Implemented |
| PaytimeStub (testing) | ✅ Implemented |
| Create boleto | ✅ Implemented |
| Cancel boleto | ✅ Implemented |
| Get status | ✅ Implemented |
| Webhook receiver | ✅ Implemented |
| Signature verification | ✅ Implemented |
| Reconciliation task | ✅ Implemented |

**Production-ready:** Yes, requires `IRIS_PAYTIME_API_KEY` and `IRIS_PAYTIME_WEBHOOK_SECRET`

### Messaging Provider

| Component | Status |
|-----------|--------|
| MessagingProviderPort | ✅ Defined |
| MessagingStub | ✅ Implemented (logs only) |
| Real WhatsApp client | ❌ Not implemented |
| Real SMS client | ❌ Not implemented |

**Production-ready:** No, stub only

### Gemini LLM

| Component | Status |
|-----------|--------|
| LLMProviderPort | ✅ Defined |
| GeminiLLMProvider | ✅ Implemented |
| StubLLMProvider | ✅ Implemented (testing) |
| Intent classification | ✅ Implemented |
| Entity extraction | ✅ Implemented |
| Structured JSON output | ✅ Enforced |

**Production-ready:** Yes, requires `IRIS_GEMINI_API_KEY`

---

## 8. Explicitly Deferred Work

The following items are **intentionally postponed**, not forgotten:

### Messaging & Communication
- WhatsApp webhook receiver
- Real WhatsApp provider integration
- SMS provider integration
- Audio transcription (speech-to-text)
- Message templates

### AI Features
- Multi-turn memory beyond 30-minute TTL
- Conversation history persistence
- Context retrieval from past conversations
- Proactive suggestions

### Collections
- Reminder scheduling use case
- Reminder sending Celery task
- Interest application use case
- Interest calculation Celery task
- Opt-out handling

### Operations
- Rate limiting (API + messaging)
- Circuit breaker for external calls
- Dead letter queue handling
- Prometheus metrics
- Analytics dashboards
- Admin UI

### Security
- OAuth / API key authentication
- Role-based access control
- Audit log table
- PII encryption at rest

---

## 9. Known Risks & Guardrails

### Risks When Resuming

| Risk | Mitigation |
|------|------------|
| Skipping confirmation gate | Never bypass — always require explicit YES |
| Interest double-application | Idempotency key per boleto + date |
| Message spam | Enforce daily limits per contact |
| Webhook replay | Check idempotency_key before processing |
| LLM hallucination | Always validate extracted entities |

### Must Never Shortcut

1. **Confirmation before money moves** — no exceptions
2. **Tenant isolation** — every query scoped
3. **Idempotency checks** — every webhook, every task
4. **Domain purity** — no SQLAlchemy in domain
5. **AI boundaries** — AI proposes, system disposes

### Architectural Rules to Respect

- Clean Architecture layers (Domain → Application → Infrastructure → Interfaces)
- DDD bounded contexts (no cross-context direct access)
- Outbox pattern for all outbound messages
- Alembic for all schema changes
- Structured logging with no PII

---

## 10. Recommended Resume Order

When development resumes, follow this sequence:

### Phase 1: Collections (High Priority)
1. Implement `ScheduleReminderUseCase`
2. Implement `SendDueRemindersTask` (Celery)
3. Implement `ApplyInterestUseCase`
4. Implement `ApplyInterestTask` (Celery)

### Phase 2: Real Messaging (High Priority)
5. Implement real WhatsApp provider (official API)
6. Implement WhatsApp webhook receiver
7. Connect AI graph to WhatsApp flow

### Phase 3: Audio Support
8. Add audio transcription provider (Whisper or equivalent)
9. Update AI graph to handle audio input

### Phase 4: Hardening
10. Add rate limiting middleware
11. Add circuit breaker for external calls
12. Add Prometheus metrics
13. Add structured audit logging

### Phase 5: Security
14. Implement API key authentication
15. Add role-based access control
16. Add PII encryption

---

## 11. Environment Variables

```bash
# Application
IRIS_APP_NAME=IRIS Billing
IRIS_APP_ENV=development|production|test
IRIS_DEBUG=true|false

# Database
IRIS_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Redis
IRIS_REDIS_URL=redis://host:6379/0

# Celery
IRIS_CELERY_BROKER_URL=redis://host:6379/1
IRIS_CELERY_RESULT_BACKEND=redis://host:6379/2

# Paytime
IRIS_PAYTIME_BASE_URL=https://api.paytime.com.br/v1
IRIS_PAYTIME_API_KEY=<required>
IRIS_PAYTIME_WEBHOOK_SECRET=<required>

# Gemini LLM
IRIS_GEMINI_API_KEY=<required>
IRIS_GEMINI_MODEL_NAME=gemini-2.5-pro
IRIS_GEMINI_TIMEOUT_SECONDS=30

# AI State
IRIS_AI_STATE_TTL_SECONDS=1800
IRIS_AI_CONFIRMATION_TTL_SECONDS=300
```

---

## 12. Final Resume Instruction

> **When resuming this project, DO NOT redesign or refactor existing foundations.**
>
> The architecture, ADRs, and implemented patterns are final.
>
> Continue strictly from this checkpoint.
>
> If you encounter something that seems wrong, check the decision log first.
> If it was decided intentionally, do not change it without explicit approval.
>
> **Start with the Collections bounded context (Phase 1).**

---

*Document generated: 2026-01-29*  
*Last development session: AI Graph Production-Ready Implementation*
