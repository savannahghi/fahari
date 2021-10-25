from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from faker import Faker
from model_bakery import baker

from fahari.users.signals import (
    BASIC_PERMISSIONS,
    account_confirmed_handler,
    assign_basic_permissions,
    email_confirmed_hander,
    is_from_whitelist_domain,
    send_admin_awaiting_approval_email,
    send_user_account_approved_email,
    send_user_awaiting_approval_email,
)

pytestmark = pytest.mark.django_db

User = get_user_model()
fake = Faker()


def test_send_user_account_approved_email(mailoutbox):
    user = baker.make(User, email=fake.email(), is_approved=False, approval_notified=False)
    assert user.approval_notified is False
    send_user_account_approved_email(user)
    assert user.approval_notified is True
    assert len(mailoutbox) >= 1  # an automatic user approval email was also sent

    expected_subject = "Fahari System Account Approved"
    expected_email = settings.SERVER_EMAIL
    successful_messages = 0
    for m in mailoutbox:
        if (
            m.subject == expected_subject
            and m.from_email == expected_email
            and user.email in list(m.to)
        ):
            successful_messages = 1

    assert successful_messages == 1


def test_send_user_awaiting_approval_email(mailoutbox):
    user = baker.make(User, email=fake.email(), is_approved=True, approval_notified=False)
    send_user_awaiting_approval_email(user)  # no error
    assert len(mailoutbox) >= 1  # an automatic user approval email was also sent
    m = mailoutbox[len(mailoutbox) - 1]
    assert m.subject == "Fahari System Account Pending Approval"
    assert m.from_email == settings.SERVER_EMAIL
    assert list(m.to) == [
        user.email,
    ]


def test_send_admin_awaiting_approval_email(mailoutbox, rf):
    admins = baker.make(
        User, 3, approval_notified=True, email=fake.email(), is_approved=True, is_staff=True
    )
    user = baker.make(User, email=fake.email(), is_approved=True, approval_notified=False)
    request = rf.get("/")
    send_admin_awaiting_approval_email(user, request)  # no error
    assert len(mailoutbox) >= 1
    m = mailoutbox[len(mailoutbox) - 1]
    assert m.subject == "New Fahari System Account Pending Approval"
    assert m.from_email == settings.SERVER_EMAIL
    assert set(m.to) == set(admin.email for admin in admins)


def test_account_confirmed_handler_newly_created():
    user = baker.make(
        User,
        email=fake.email(),
    )
    assert account_confirmed_handler(User, user, created=True) is None


def test_account_confirmed_handler_not_approved():
    user = baker.make(User, email=fake.email(), is_approved=False)
    assert account_confirmed_handler(User, user, created=False) is None


def test_account_confirmed_handler_already_notified():
    user = baker.make(User, email=fake.email(), is_approved=True, approval_notified=True)
    assert account_confirmed_handler(User, user, created=False) is None


def test_account_confirmed_handler_happy_case(mailoutbox):
    user = baker.make(User, email=fake.email(), is_approved=False, approval_notified=False)
    assert user.approval_notified is False

    user.is_approved = True
    user.save()

    assert account_confirmed_handler(User, user, created=False) in [True, None]
    assert user.approval_notified is True
    assert len(mailoutbox) >= 1

    expected_subject = "Fahari System Account Approved"
    expected_email = settings.SERVER_EMAIL
    successful_messages = 0
    for m in mailoutbox:
        if (
            m.subject == expected_subject
            and m.from_email == expected_email
            and user.email in list(m.to)
        ):
            successful_messages = 1

    assert successful_messages == 1


def test_email_confirmed_handler_user_does_not_exist():
    fake_email = fake.email()
    request = MagicMock()
    assert email_confirmed_hander(request, fake_email) is False


def test_email_confirmed_handler_approved_user():
    approved_user = baker.make(User, email=fake.email(), is_approved=True)
    request = MagicMock()
    email = approved_user.email
    assert email_confirmed_hander(request, email) is False


def test_email_confirmed_handler_user_awaiting_approval():
    approved_user = baker.make(User, email=fake.email(), is_approved=False)
    request = MagicMock()
    email = approved_user.email
    assert email_confirmed_hander(request, email) is True


def test_assign_basic_permission():
    user = baker.make(User, email=fake.email(), is_approved=False)
    assign_basic_permissions(user)
    perms = user.get_user_permissions()
    assert len(perms) == len(BASIC_PERMISSIONS)
    for perm in BASIC_PERMISSIONS:
        assert user.has_perm(perm)


def test_is_from_whitelist_domain():
    assert is_from_whitelist_domain("ngure@savannahghi.org") is True
    assert is_from_whitelist_domain("kalulu@juha.com") is False


def test_account_confirmed_handler_newly_created_whitelist_user():
    user = baker.make(
        User,
        email="noreply@savannahghi.org",
    )
    assert account_confirmed_handler(User, user, created=True) is None
