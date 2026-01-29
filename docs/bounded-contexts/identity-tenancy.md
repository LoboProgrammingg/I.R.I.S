# Identity & Tenancy Bounded Context

**Status:** Active  
**Version:** 1.0  
**Date:** 2026-01-29

---

## 1. Purpose

The Identity & Tenancy context provides the foundational layer for:
- **Multi-tenant isolation** — All data in the system is scoped by tenant
- **User management** — Users belong to tenants and initiate actions
- **Authentication context** — Establishes who is performing operations

This context is the **foundation** for all other bounded contexts.

---

## 2. Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Tenant lifecycle | Create, activate, deactivate tenants |
| User management | Register users within a tenant |
| Tenant scoping | Provide tenant_id for all downstream operations |
| Identity validation | Ensure user belongs to claimed tenant |

### 2.1 What This Context Does NOT Do

- Authentication (JWT, OAuth) — handled by infrastructure
- Authorization (roles, permissions) — minimal MVP, expand later
- Session management — handled by infrastructure

---

## 3. Entities

### 3.1 Tenant (Aggregate Root)

The logical customer/account that owns all data.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | TenantId (UUID) | Unique identifier |
| `name` | str | Tenant display name |
| `is_active` | bool | Whether tenant can operate |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

### 3.2 User (Entity)

A human operator within a tenant.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UserId (UUID) | Unique identifier |
| `tenant_id` | TenantId | Owning tenant |
| `phone_number` | PhoneNumber | E.164 normalized phone |
| `name` | str | Display name |
| `role` | UserRole | admin or user |
| `is_active` | bool | Whether user can operate |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

---

## 4. Value Objects

| Value Object | Description |
|--------------|-------------|
| `TenantId` | Strongly-typed UUID for tenant |
| `UserId` | Strongly-typed UUID for user |
| `PhoneNumber` | E.164 normalized phone number |
| `UserRole` | Enum: ADMIN, USER |

---

## 5. Invariants (Business Rules)

### 5.1 Tenant Invariants

1. **Tenant name must not be empty**
2. **Tenant ID is immutable after creation**
3. **Inactive tenants cannot have active users**

### 5.2 User Invariants

1. **User must belong to exactly one tenant**
2. **Phone number must be unique within a tenant**
3. **Phone number must be valid E.164 format**
4. **User role must be explicitly set**
5. **User ID is immutable after creation**
6. **Inactive users cannot perform operations**

---

## 6. Domain Events

| Event | Trigger |
|-------|---------|
| `TenantCreated` | New tenant registered |
| `TenantDeactivated` | Tenant disabled |
| `UserRegistered` | New user added to tenant |
| `UserDeactivated` | User disabled |

---

## 7. Repository Ports

### 7.1 TenantRepository

```python
get_by_id(tenant_id: TenantId) -> Tenant | None
save(tenant: Tenant) -> Tenant
exists(tenant_id: TenantId) -> bool
```

### 7.2 UserRepository

```python
get_by_id(user_id: UserId) -> User | None
get_by_phone(tenant_id: TenantId, phone: PhoneNumber) -> User | None
save(user: User) -> User
list_by_tenant(tenant_id: TenantId) -> list[User]
phone_exists_in_tenant(tenant_id: TenantId, phone: PhoneNumber) -> bool
```

---

## 8. Dependencies

- **Upstream:** None (foundational context)
- **Downstream:** All other contexts depend on Identity & Tenancy

---

## 9. Notes

- MVP scope: minimal user roles (ADMIN, USER)
- Future: fine-grained permissions, team hierarchy
- Phone number is primary identifier for WhatsApp integration
