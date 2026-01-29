"""Unit tests for Identity entities."""

import pytest

from app.domain.identity.entities.tenant import Tenant
from app.domain.identity.entities.user import User
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.identity.value_objects.user_role import UserRole


class TestTenant:
    """Tests for Tenant aggregate root."""

    def test_create_with_valid_name(self) -> None:
        tenant = Tenant.create(name="Acme Corp")
        assert tenant.name == "Acme Corp"
        assert tenant.is_active is True

    def test_create_strips_whitespace(self) -> None:
        tenant = Tenant.create(name="  Acme Corp  ")
        assert tenant.name == "Acme Corp"

    def test_create_with_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name must not be empty"):
            Tenant.create(name="")

    def test_create_with_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="name must not be empty"):
            Tenant.create(name="   ")

    def test_deactivate(self) -> None:
        tenant = Tenant.create(name="Acme Corp")
        tenant.deactivate()
        assert tenant.is_active is False

    def test_activate(self) -> None:
        tenant = Tenant.create(name="Acme Corp")
        tenant.deactivate()
        tenant.activate()
        assert tenant.is_active is True

    def test_rename(self) -> None:
        tenant = Tenant.create(name="Acme Corp")
        tenant.rename("Acme Inc")
        assert tenant.name == "Acme Inc"

    def test_rename_with_empty_raises(self) -> None:
        tenant = Tenant.create(name="Acme Corp")
        with pytest.raises(ValueError, match="name must not be empty"):
            tenant.rename("")

    def test_equality_by_id(self) -> None:
        tenant_id = TenantId.generate()
        t1 = Tenant.create(name="Acme", tenant_id=tenant_id)
        t2 = Tenant.create(name="Different", tenant_id=tenant_id)
        assert t1 == t2


class TestUser:
    """Tests for User entity."""

    def test_create_with_valid_data(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        user = User.create(
            tenant_id=tenant_id,
            phone_number=phone,
            name="John Doe",
        )
        assert user.name == "John Doe"
        assert user.tenant_id == tenant_id
        assert user.phone_number == phone
        assert user.role == UserRole.USER
        assert user.is_active is True

    def test_create_with_admin_role(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        user = User.create(
            tenant_id=tenant_id,
            phone_number=phone,
            name="Admin User",
            role=UserRole.ADMIN,
        )
        assert user.role == UserRole.ADMIN
        assert user.is_admin() is True

    def test_create_with_empty_name_raises(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        with pytest.raises(ValueError, match="name must not be empty"):
            User.create(tenant_id=tenant_id, phone_number=phone, name="")

    def test_deactivate(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        user = User.create(tenant_id=tenant_id, phone_number=phone, name="John")
        user.deactivate()
        assert user.is_active is False
        assert user.can_operate() is False

    def test_change_role(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        user = User.create(tenant_id=tenant_id, phone_number=phone, name="John")
        user.change_role(UserRole.ADMIN)
        assert user.role == UserRole.ADMIN

    def test_rename(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        user = User.create(tenant_id=tenant_id, phone_number=phone, name="John")
        user.rename("Jane Doe")
        assert user.name == "Jane Doe"
