import pytest

from fahari.users.models import User

pytestmark = pytest.mark.django_db


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.username}/"


def test_user_permissions_no_permissions(user):
    assert user.permissions == "-"


def test_user_permissions_with_permissions(user_with_all_permissions):
    assert len(user_with_all_permissions.permissions) > 2


def test_user_permissions_with_permissions_via_groups(user_with_group):
    assert len(user_with_group.permissions) > 2


def test_user_groups_no_groups(user):
    assert user.gps == "-"


def test_user_groups_with_groups(user_with_group):
    assert len(user_with_group.gps) > 2
