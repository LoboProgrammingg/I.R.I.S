---
trigger: always_on
---

# IRIS / Paytime AI Billing System — Domain Glossary (Ubiquitous Language)

## Purpose
This document defines the **official ubiquitous language** of the system.

All:
- Code
- Database models
- API payloads
- Logs
- AI prompts
- Documentation
- Conversations with stakeholders

MUST use the terms defined here.

If a term is not in this glossary:
- Do not invent it
- Propose it explicitly before usage

---

## 1. Core Actors

### Tenant
**Definition:**  
A logical customer/account that owns data, configuration, and users.

**Notes:**
- All data is scoped by tenant
- Tenants never share data

---

### User
**Definition:**  
A human authorized to operate the system on behalf of a tenant.

**Notes:**
- Initiates actions via WhatsApp or UI
- Must explicitly confirm financial actions

---

### Contact
**Definition:**  
A person or entity that can receive a boleto.

**Attributes:**
- Name
- Phone number (E.164)
- Optional metadata

**Rules:**
- Contacts belong to a tenant
- Contacts may be ambiguous and require confirmation

---

## 2. Billing & Payments

### Boleto
**Definition:**  
A billing instrument generated via Paytime that represents a payment request.

**Attributes:**
- Amount
- Due date
- Status
- External reference (Paytime ID)
- Payer (Contact)

**States:**
- CREATED
- SENT
- PAID
- OVERDUE
- CANCELLED
- FAILED

**Rules:**
- A boleto is immutable after PAID
- A boleto must never be created without validation and confirmation

---

### Payment
**Definition:**  
A confirmed monetary settlement of a boleto.

**Attributes:**
- Amount
- Payment date
- External confirmation (Paytime event)

**Rules:**
- Payments are recorded via Paytime webhook or reconciliation job
- One boleto may have only one final payment

---

### Interest Policy
**Definition:**  
A configuration defining how penalties or interest are applied to overdue boletos.

**Attributes:**
- Grace period
- Daily interest rate
- Fixed penalty (optional)

**Rules:**
- Must be explicitly configured
- Never inferred by AI
- Changes are auditable

---

## 3. Collections & Reminders

### Reminder
**Definition:**  
A scheduled message sent to a contact to request boleto payment.

**Attributes:**
- Scheduled date
- Channel
- Status

**Rules:**
- Reminders stop immediately on payment or cancellation
- Rate limits and opt-out rules apply

---

### Delinquency
**Definition:**  
The state of a boleto after its due date has passed without payment.

**Rules:**
- Triggers interest policy
- Triggers reminder escalation logic

---

## 4. Finance & Ledger

### Ledger
**Definition:**  
The financial record system tracking income and expenses.

**Notes:**
- Used for summaries and reporting
- Does not replace accounting software

---

### Ledger Transaction
**Definition:**  
A single financial entry representing money in or out.

**Types:**
- INCOME
- EXPENSE

**Rules:**
- Payments generate income transactions
- Manual expenses require user confirmation

---

## 5. Messaging

### Messaging Provider
**Definition:**  
An abstraction responsible for delivering outbound messages.

**Examples:**
- Official WhatsApp API
- WhatsApp automation sender
- (Future) SMS / Email

---

### Message Outbox Item
**Definition:**  
A persisted record representing a message that must be delivered.

**Attributes:**
- Recipient
- Payload
- Status (PENDING, SENT, FAILED)
- Attempts

**Rules:**
- Must exist before sending
- Enables retries and auditing

---

## 6. AI & Automation

### AI Orchestrator
**Definition:**  
The component responsible for coordinating AI behavior.

**Responsibilities:**
- Intent classification
- Entity extraction
- Tool selection
- Confirmation handling

**Non-Responsibilities:**
- Business logic
- Direct DB access
- External API execution

---

### Tool
**Definition:**  
A deterministic system operation that can be invoked by the AI.

**Examples:**
- CreateBoleto
- SendBoleto
- ScheduleReminder
- RecordLedgerTransaction

---

### Confirmation
**Definition:**  
An explicit user approval required before executing a financial action.

**Rules:**
- Required for all monetary operations
- Must be unambiguous
- Must be recorded

---

## 7. Technical Concepts (Contextualized)

### Idempotency Key
**Definition:**  
A unique identifier used to ensure operations are executed only once.

**Usage:**
- Webhooks
- Boleto creation
- Message sending

---

### Domain Event
**Definition:**  
A record of something that has happened in the domain.

**Examples:**
- BoletoCreated
- BoletoPaid
- ReminderSent

**Rules:**
- Used for auditing and async reactions
- Not used for synchronous logic flow

---

## 8. States & Statuses (Canonical)

### Boleto Status
- CREATED
- SENT
- PAID
- OVERDUE
- CANCELLED
- FAILED

### Reminder Status
- SCHEDULED
- SENT
- FAILED
- CANCELLED

### Message Status
- PENDING
- SENT
- FAILED
- RETRYING

---

## 9. Forbidden Terms & Anti-Language

The following terms must NOT be used:
- “Customer” (use Tenant or Contact)
- “Service” (unless clearly bounded)
- “Manager”
- “Helper”
- “Magic”
- “Auto” (without explicit rule definition)

Ambiguous language creates bugs.

---

## 10. Evolution Rules

- This glossary is **versioned**
- Changes require:
  - Explicit discussion
  - Documentation update
- Backward-incompatible changes must be justified

---

## Final Principle

> **If you cannot name it precisely, you cannot model it correctly.**

This glossary exists to protect the system from ambiguity, miscommunication, and future technical debt.

---

## Compliance Statement
All system components must comply with:
- `knowledge.md`
- `architecture.md`
- `ai-behavior.md`
- `security.md`
- `pr-checklist.md`
- This document (`domain-glossary.md`)

In case of conflict, the most restrictive definition prevails.
