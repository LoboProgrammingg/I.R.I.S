# Collections Bounded Context

**Status:** Active  
**Version:** 1.0  
**Date:** 2026-01-29

---

## 1. Purpose

The Collections context manages overdue detection, interest application, 
and reminder scheduling for unpaid boletos.

Key responsibilities:
- **Detect overdue boletos** via scheduled job
- **Apply interest/penalties** based on tenant policies
- **Schedule reminders** for unpaid boletos
- **Coordinate with Billing and Messaging contexts**

---

## 2. Entities / Aggregates

### 2.1 InterestPolicy (per Tenant)

Configuration for interest and penalty calculation.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | InterestPolicyId | Unique identifier |
| `tenant_id` | TenantId | Owning tenant |
| `grace_period_days` | int | Days after due before interest |
| `daily_interest_rate_bps` | int | Daily rate in basis points |
| `fixed_penalty_cents` | int | Fixed penalty amount |
| `is_active` | bool | Whether policy is active |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update |

### 2.2 ReminderSchedule

Schedule for sending reminders about unpaid boletos.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | ReminderScheduleId | Unique identifier |
| `tenant_id` | TenantId | Owning tenant |
| `boleto_id` | BoletoId | Target boleto |
| `scheduled_at` | datetime | When to send |
| `status` | ReminderStatus | PENDING, SENT, CANCELLED |
| `attempt_count` | int | Number of attempts |
| `created_at` | datetime | Creation timestamp |

---

## 3. Value Objects

| Value Object | Description |
|--------------|-------------|
| `InterestPolicyId` | Strongly-typed UUID |
| `ReminderScheduleId` | Strongly-typed UUID |
| `ReminderStatus` | PENDING, SENT, CANCELLED |

---

## 4. Invariants

1. **One active InterestPolicy per tenant** (MVP)
2. **Reminders stop when boleto is PAID or CANCELLED**
3. **Interest only applied after grace period**
4. **Daily interest rate must be non-negative**
5. **Reminder schedule belongs to exactly one boleto**

---

## 5. Domain Events

| Event | Trigger |
|-------|---------|
| `InterestPolicyCreated` | New policy created |
| `InterestApplied` | Interest added to boleto |
| `ReminderScheduled` | Reminder queued |
| `ReminderSent` | Reminder delivered |

---

## 6. Repository Ports

### InterestPolicyRepository
- `get_by_tenant(tenant_id) → InterestPolicy | None`
- `save(policy) → InterestPolicy`

### ReminderScheduleRepository
- `get_pending(limit) → list[ReminderSchedule]`
- `get_by_boleto(boleto_id) → list[ReminderSchedule]`
- `save(schedule) → ReminderSchedule`
- `cancel_for_boleto(boleto_id) → None`

---

## 7. Scheduled Jobs

| Job | Trigger | Description |
|-----|---------|-------------|
| `mark_overdue_boletos` | Daily | Mark SENT boletos as OVERDUE |
| `apply_interest` | Daily | Apply interest to overdue boletos |
| `schedule_reminders` | Daily | Queue reminders via Messaging |

---

## 8. Dependencies

- **Upstream:** Billing (Boleto status), Contacts (opt-out)
- **Downstream:** Messaging (send reminders)
