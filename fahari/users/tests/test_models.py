import pytest

from fahari.users.models import User, default_organisation

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.username}/"


def test_user_permissions_with_permissions(user_with_all_permissions):
    assert len(user_with_all_permissions.permissions) > 2


def test_user_permissions_with_permissions_via_groups(user_with_group):
    assert len(user_with_group.permissions) > 2


def test_user_groups_no_groups(user):
    assert user.gps == "-"


def test_user_groups_with_groups(user_with_group):
    assert len(user_with_group.gps) > 2


def test_default_organisation():
    first_fetch_org = default_organisation()
    second_fetch_org = default_organisation()
    assert first_fetch_org == second_fetch_org
