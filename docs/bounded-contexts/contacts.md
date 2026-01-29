# Contacts Bounded Context

**Status:** Active  
**Version:** 1.0  
**Date:** 2026-01-29

---

## 1. Purpose

The Contacts context manages the registry of people/entities that can receive boletos and messages.

Key responsibilities:
- **Store tenant-scoped contacts** — All contacts belong to exactly one tenant
- **Phone number validation** — Normalize and validate E.164 format
- **Enable lookups** — For billing (boleto creation) and messaging
- **Messaging compliance** — Support opt-out flag

---

## 2. Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Contact lifecycle | Create, update, deactivate contacts |
| Phone normalization | Ensure E.164 format |
| Tenant scoping | Contacts belong to exactly one tenant |
| Opt-out management | Track messaging preferences |
| Lookup by phone | Find contacts for billing/messaging |

### 2.1 What This Context Does NOT Do

- Send messages (Messaging context)
- Create boletos (Billing context)
- Manage users (Identity context)

---

## 3. Entities

### 3.1 Contact (Aggregate Root)

A person or entity that can receive boletos.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | ContactId (UUID) | Unique identifier |
| `tenant_id` | TenantId | Owning tenant |
| `phone_number` | PhoneNumber | E.164 normalized phone |
| `name` | str | Display name |
| `email` | str \| None | Optional email |
| `is_active` | bool | Whether contact is active |
| `opted_out` | bool | Messaging opt-out flag |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

---

## 4. Value Objects

| Value Object | Description |
|--------------|-------------|
| `ContactId` | Strongly-typed UUID for contact |
| `PhoneNumber` | E.164 normalized (reused from Identity) |
| `TenantId` | Tenant reference (reused from Identity) |

---

## 5. Invariants (Business Rules)

### 5.1 Contact Invariants

1. **Contact must belong to exactly one tenant**
2. **Phone number must be unique within a tenant**
3. **Phone number must be valid E.164 format**
4. **Contact name must not be empty**
5. **Contact ID is immutable after creation**
6. **Opted-out contacts cannot receive marketing messages**

---

## 6. Domain Events

| Event | Trigger |
|-------|---------|
| `ContactCreated` | New contact registered |
| `ContactUpdated` | Contact information changed |
| `ContactDeactivated` | Contact disabled |
| `ContactOptedOut` | Contact opted out of messaging |
| `ContactOptedIn` | Contact opted back in |

---

## 7. Repository Ports

### 7.1 ContactRepository

```python
get_by_id(contact_id: ContactId) -> Contact | None
get_by_phone(tenant_id: TenantId, phone: PhoneNumber) -> Contact | None
save(contact: Contact) -> Contact
list_by_tenant(tenant_id: TenantId) -> list[Contact]
phone_exists_in_tenant(tenant_id: TenantId, phone: PhoneNumber) -> bool
```

---

## 8. Dependencies

- **Upstream:** Identity & Tenancy (TenantId, PhoneNumber)
- **Downstream:** Billing, Messaging, Collections

---

## 9. Notes

- Reuses `PhoneNumber` and `TenantId` from Identity context
- `opted_out` flag is critical for messaging compliance
- Future: fuzzy name matching for AI contact resolution
