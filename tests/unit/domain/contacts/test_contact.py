"""Unit tests for Contact entity."""

import pytest

from app.domain.contacts.entities.contact import Contact
from app.domain.contacts.value_objects.contact_id import ContactId
from app.domain.identity.value_objects.phone_number import PhoneNumber
from app.domain.identity.value_objects.tenant_id import TenantId


class TestContactId:
    """Tests for ContactId value object."""

    def test_generate_creates_valid_id(self) -> None:
        contact_id = ContactId.generate()
        assert contact_id.value is not None

    def test_from_string_parses_valid_uuid(self) -> None:
        uuid_str = "12345678-1234-5678-1234-567812345678"
        contact_id = ContactId.from_string(uuid_str)
        assert str(contact_id) == uuid_str

    def test_equality(self) -> None:
        uuid_str = "12345678-1234-5678-1234-567812345678"
        id1 = ContactId.from_string(uuid_str)
        id2 = ContactId.from_string(uuid_str)
        assert id1 == id2


class TestContact:
    """Tests for Contact aggregate root."""

    def test_create_with_valid_data(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(
            tenant_id=tenant_id,
            phone_number=phone,
            name="John Doe",
        )
        assert contact.name == "John Doe"
        assert contact.tenant_id == tenant_id
        assert contact.phone_number == phone
        assert contact.is_active is True
        assert contact.opted_out is False

    def test_create_with_email(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(
            tenant_id=tenant_id,
            phone_number=phone,
            name="John Doe",
            email="john@example.com",
        )
        assert contact.email == "john@example.com"

    def test_create_with_empty_name_raises(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        with pytest.raises(ValueError, match="name must not be empty"):
            Contact.create(tenant_id=tenant_id, phone_number=phone, name="")

    def test_deactivate(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(tenant_id=tenant_id, phone_number=phone, name="John")
        contact.deactivate()
        assert contact.is_active is False

    def test_opt_out(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(tenant_id=tenant_id, phone_number=phone, name="John")
        contact.opt_out()
        assert contact.opted_out is True
        assert contact.can_receive_messages() is False

    def test_opt_in(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(tenant_id=tenant_id, phone_number=phone, name="John")
        contact.opt_out()
        contact.opt_in()
        assert contact.opted_out is False
        assert contact.can_receive_messages() is True

    def test_can_receive_messages_when_active_and_not_opted_out(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(tenant_id=tenant_id, phone_number=phone, name="John")
        assert contact.can_receive_messages() is True

    def test_cannot_receive_messages_when_inactive(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(tenant_id=tenant_id, phone_number=phone, name="John")
        contact.deactivate()
        assert contact.can_receive_messages() is False

    def test_rename(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(tenant_id=tenant_id, phone_number=phone, name="John")
        contact.rename("Jane Doe")
        assert contact.name == "Jane Doe"

    def test_update_email(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact = Contact.create(tenant_id=tenant_id, phone_number=phone, name="John")
        contact.update_email("john@example.com")
        assert contact.email == "john@example.com"

    def test_equality_by_id(self) -> None:
        tenant_id = TenantId.generate()
        phone = PhoneNumber("+5511999998888")
        contact_id = ContactId.generate()
        c1 = Contact.create(
            tenant_id=tenant_id, phone_number=phone, name="John", contact_id=contact_id
        )
        c2 = Contact.create(
            tenant_id=tenant_id, phone_number=phone, name="Different", contact_id=contact_id
        )
        assert c1 == c2
