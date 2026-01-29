# Messaging Bounded Context

**Status:** Active  
**Version:** 1.0  
**Date:** 2026-01-29

---

## 1. Purpose

The Messaging context manages the reliable delivery of outbound messages 
using the **Outbox Pattern**.

Key responsibilities:
- **Queue messages** for delivery
- **Track delivery status** through lifecycle
- **Retry failed deliveries** with backoff
- **Respect opt-out preferences**
- **Abstract messaging providers** (WhatsApp, SMS, etc.)

---

## 2. Entities / Aggregates

### 2.1 MessageOutboxItem (Aggregate Root)

A message queued for delivery.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | OutboxItemId | Unique identifier |
| `tenant_id` | TenantId | Owning tenant |
| `contact_id` | ContactId | Recipient contact |
| `message_type` | MessageType | Type of message |
| `status` | DeliveryStatus | Current delivery status |
| `payload` | dict | Message content |
| `idempotency_key` | str | Prevents duplicates |
| `attempt_count` | int | Number of delivery attempts |
| `last_error` | str \| None | Last error message |
| `scheduled_at` | datetime | When to deliver |
| `sent_at` | datetime \| None | When delivered |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update |

---

## 3. Value Objects

| Value Object | Description |
|--------------|-------------|
| `OutboxItemId` | Strongly-typed UUID |
| `MessageType` | BOLETO_SEND, REMINDER, NOTIFICATION |
| `DeliveryStatus` | PENDING, SENT, FAILED, RETRYING |

---

## 4. Invariants

1. **Outbox item belongs to exactly one tenant**
2. **Opted-out contacts must not receive messages** (checked in application layer)
3. **Idempotency key must be unique per tenant**
4. **Attempt count incremented safely on retry**
5. **SENT items are immutable**

---

## 5. Status Transitions

```
PENDING → SENT
PENDING → FAILED
PENDING → RETRYING
RETRYING → SENT
RETRYING → FAILED
```

---

## 6. Domain Events

| Event | Trigger |
|-------|---------|
| `MessageQueued` | New message added to outbox |
| `MessageSent` | Message delivered successfully |
| `MessageFailed` | Delivery failed (final) |

---

## 7. Repository Ports

### OutboxRepository
- `get_by_id(item_id) → MessageOutboxItem | None`
- `save(item) → MessageOutboxItem`
- `get_pending(tenant_id, limit) → list[MessageOutboxItem]`
- `exists_by_idempotency_key(tenant_id, key) → bool`

---

## 8. Provider Ports

### MessagingProviderPort
- `send(recipient, message_type, payload) → ProviderResult`

> **Note:** Provider implementation is a stub for MVP.
> Real WhatsApp integration comes later.

---

## 9. Dependencies

- **Upstream:** Identity (TenantId), Contacts (ContactId, opt-out check)
- **Downstream:** Billing (boleto send triggers), Collections (reminders)
