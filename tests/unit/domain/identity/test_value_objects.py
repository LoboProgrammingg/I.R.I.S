"""Unit tests for Identity value objects."""

import pytest
from uuid import UUID

from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId
from app.domain.identity.value_objects.user_id import UserId
from app.domain.identity.value_objects.user_role import UserRole


class TestTenantId:
    """Tests for TenantId value object."""

    def test_generate_creates_valid_uuid(self) -> None:
        tenant_id = TenantId.generate()
        assert isinstance(tenant_id.value, UUID)

    def test_from_string_parses_valid_uuid(self) -> None:
        uuid_str = "12345678-1234-5678-1234-567812345678"
        tenant_id = TenantId.from_string(uuid_str)
        assert str(tenant_id) == uuid_str

    def test_from_string_raises_on_invalid(self) -> None:
        with pytest.raises(ValueError):
            TenantId.from_string("not-a-uuid")

    def test_equality(self) -> None:
        uuid_str = "12345678-1234-5678-1234-567812345678"
        id1 = TenantId.from_string(uuid_str)
        id2 = TenantId.from_string(uuid_str)
        assert id1 == id2

    def test_immutability(self) -> None:
        tenant_id = TenantId.generate()
        with pytest.raises(AttributeError):
            tenant_id.value = UUID("12345678-1234-5678-1234-567812345678")


class TestUserId:
    """Tests for UserId value object."""

    def test_generate_creates_valid_uuid(self) -> None:
        user_id = UserId.generate()
        assert isinstance(user_id.value, UUID)

    def test_from_string_parses_valid_uuid(self) -> None:
        uuid_str = "87654321-4321-8765-4321-876543218765"
        user_id = UserId.from_string(uuid_str)
        assert str(user_id) == uuid_str


class TestPhoneNumber:
    """Tests for PhoneNumber value object."""

    def test_valid_e164_format(self) -> None:
        phone = PhoneNumber("+5511999998888")
        assert phone.value == "+5511999998888"

    def test_from_string_normalizes(self) -> None:
        phone = PhoneNumber.from_string("55 11 99999-8888")
        assert phone.value == "+5511999998888"

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValueError):
            PhoneNumber("12345")

    def test_masked_hides_middle_digits(self) -> None:
        phone = PhoneNumber("+5511999998888")
        assert phone.masked() == "+55******8888"

    def test_equality(self) -> None:
        phone1 = PhoneNumber("+5511999998888")
        phone2 = PhoneNumber("+5511999998888")
        assert phone1 == phone2


class TestUserRole:
    """Tests for UserRole enum."""

    def test_admin_is_admin(self) -> None:
        assert UserRole.ADMIN.is_admin() is True

    def test_user_is_not_admin(self) -> None:
        assert UserRole.USER.is_admin() is False
