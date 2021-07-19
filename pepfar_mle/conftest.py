import pytest
from django.contrib.auth.models import Group, Permission
from model_bakery import baker

from pepfar_mle.users.models import User
from pepfar_mle.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def user_with_all_permissions(user) -> User:
    all_perms = Permission.objects.all()
    for perm in all_perms:
        user.user_permissions.add(perm)
    user.save()
    return user


@pytest.fixture
def group_with_all_permissions() -> Group:
    group = baker.make(Group)
    all_perms = Permission.objects.all()
    for perm in all_perms:
        group.permissions.add(perm)

    group.save()
    return group


@pytest.fixture
def user_with_group(user, group_with_all_permissions) -> User:
    user.groups.add(group_with_all_permissions)
    user.save()
    return user
