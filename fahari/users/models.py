import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import PROTECT, BooleanField, CharField, ForeignKey, UUIDField
from django.db.utils import ProgrammingError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

DEFAULT_ORG_ID = "4181df12-ca96-4f28-b78b-8e8ad88b25df"
DEFAULT_ORG_CODE = 1


def default_organisation():
    try:
        from fahari.common.models import Organisation  # intentional late imoort

        org, _ = Organisation.objects.get_or_create(
            code=DEFAULT_ORG_CODE,
            id=DEFAULT_ORG_ID,
            defaults={
                "organisation_name": settings.ORGANISATION_NAME,
                "email_address": settings.ORGANISATION_EMAIL,
                "phone_number": settings.ORGANISATION_PHONE,
            },
        )
        return org.pk
    except (ProgrammingError, Exception):  # pragma: nocover
        # this will occur during initial migrations on a clean db
        return DEFAULT_ORG_ID


class User(AbstractUser):
    """Default user model."""

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    is_approved = BooleanField(
        default=False,
        help_text="When true, the user is able to log in to the main website (and vice versa)",
    )
    approval_notified = BooleanField(
        default=False,
        help_text="When true, the user has been notified that their account is approved",
    )
    phone = PhoneNumberField(null=True, blank=True)
    organisation = ForeignKey(
        "common.Organisation",
        on_delete=PROTECT,
        default=default_organisation,
    )

    @property
    def permissions(self):
        perms = set(
            [
                f"{perm.content_type.app_label}.{perm.codename}"
                for perm in self.user_permissions.all()
            ]
        )
        groups = self.groups.all()
        for group in groups:
            group_perms = set(
                [
                    f"{perm.content_type.app_label}.{perm.codename}"
                    for perm in group.permissions.all()
                ]
            )
            perms = perms | group_perms
        return ",\n".join(list(perms))

    @property
    def gps(self):
        groups = [gp.name for gp in self.groups.all()]
        return ",".join(groups) or "-"

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    class Meta(AbstractUser.Meta):
        permissions = [
            ("can_view_dashboard", "Can View Dashboard"),
            ("can_view_about", "Can View About Page"),
        ]
