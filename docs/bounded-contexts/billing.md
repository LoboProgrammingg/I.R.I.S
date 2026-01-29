# Billing Bounded Context

**Status:** Active  
**Version:** 1.1  
**Date:** 2026-01-29

---

## 1. Purpose

The Billing context manages the creation, lifecycle, and payment of boletos.

Key responsibilities:
- **Create boletos** for contacts within a tenant
- **Track boleto status** through its lifecycle
- **Record payments** when boletos are paid
- **Enforce financial invariants**

---

## 2. Entities / Aggregates

### 2.1 Boleto (Aggregate Root)

A payment request instrument generated for a contact.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | BoletoId | Unique identifier |
| `tenant_id` | TenantId | Owning tenant |
| `contact_id` | ContactId | Payer contact |
| `amount` | Money | Amount to be paid |
| `due_date` | DueDate | Payment due date |
| `status` | BoletoStatus | Current status |
| `idempotency_key` | str | Prevents duplicates |
| `provider_reference` | str \| None | Provider (Paytime) reference |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update |

### 2.2 Payment (Entity)

A confirmed payment for a boleto.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | PaymentId | Unique identifier |
| `boleto_id` | BoletoId | Associated boleto |
| `amount` | Money | Amount paid |
| `paid_at` | datetime | Payment timestamp |
| `provider_reference` | str \| None | Provider reference |

---

## 3. Value Objects

| Value Object | Description |
|--------------|-------------|
| `BoletoId` | Strongly-typed UUID |
| `PaymentId` | Strongly-typed UUID |
| `Money` | Amount in cents + currency (BRL) |
| `DueDate` | Validated due date |
| `BoletoStatus` | CREATED, SENT, PAID, OVERDUE, CANCELLED |

---

## 4. Invariants

1. **Boleto belongs to exactly one tenant**
2. **Boleto references exactly one contact**
3. **A PAID boleto is immutable** (no status changes allowed)
4. **Status transitions must be valid** (state machine)
5. **One boleto = one payment** (MVP)
6. **Amount must be positive**
7. **Due date must be in the future** (at creation)
8. **Idempotency key must be unique per tenant**

---

## 5. Status Transitions

```
CREATED → SENT → PAID
CREATED → SENT → OVERDUE → PAID
CREATED → CANCELLED
SENT → CANCELLED
OVERDUE → CANCELLED
```

### 5.1 Transition Rules

| From | To | Description |
|------|-----|-------------|
| CREATED | SENT | Boleto sent to contact via messaging |
| CREATED | CANCELLED | Boleto cancelled before sending |
| SENT | PAID | Payment confirmed via webhook |
| SENT | OVERDUE | Due date passed (scheduled job) |
| SENT | CANCELLED | Boleto cancelled after sending |
| OVERDUE | PAID | Late payment received |
| OVERDUE | CANCELLED | Boleto cancelled after overdue |

### 5.2 Terminal States

- **PAID** — No further transitions allowed
- **CANCELLED** — No further transitions allowed

### 5.3 Overdue Semantics

> **Important:** Overdue status is applied by a **scheduled background job** 
> in the **Collections** bounded context (not yet implemented).
>
> The job runs daily and marks SENT boletos as OVERDUE when `due_date < today`.
> Late payments (OVERDUE → PAID) are still allowed.

---

## 6. Domain Events

| Event | Trigger |
|-------|---------|
| `BoletoCreated` | New boleto created |
| `BoletoSent` | Boleto sent to contact |
| `BoletoPaid` | Payment confirmed |
| `BoletoOverdueMarked` | Boleto marked as overdue by scheduled job |
| `BoletoCancelled` | Boleto cancelled |

---

## 7. Cancellation Semantics

Cancellation is a **logical status change only**.

### What cancellation DOES:
- Marks boleto status as CANCELLED
- Stops further reminders (Messaging context)
- Prevents new payments from being recorded

### What cancellation does NOT do:
- Does NOT create or modify Payment records
- Does NOT issue refunds or chargebacks
- Does NOT interact with Paytime for reversal

> **Refunds and chargebacks are out of scope for MVP.**
> If needed in the future, they will be a separate domain operation.

---

## 8. Repository Ports

### BoletoRepository
- `get_by_id(boleto_id) → Boleto | None`
- `save(boleto) → Boleto`
- `exists_by_idempotency_key(tenant_id, key) → bool`

### PaymentRepository
- `get_by_boleto_id(boleto_id) → Payment | None`
- `save(payment) → Payment`

---

## 8. Dependencies

- **Upstream:** Identity (TenantId), Contacts (ContactId)
- **Downstream:** Collections, Messaging
