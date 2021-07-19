import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField, CharField, UUIDField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for PEPFAR Monitoring, Learning and Evaluation."""

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    is_approved = BooleanField(
        default=False,
        help_text="When true, the user is able to log in to the main website (and vice versa)",
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
        return ",\n".join(list(perms)) or "-"

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
