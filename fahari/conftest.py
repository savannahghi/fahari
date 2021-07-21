import pytest
from django.contrib.auth.models import Group, Permission
from model_bakery import baker

from fahari.users.models import User
from fahari.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(autouse=True)
def test_email_backend(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


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
def staff_user(user_with_all_permissions) -> User:
    user_with_all_permissions.is_staff = True
    user_with_all_permissions.save()
    return user_with_all_permissions


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
