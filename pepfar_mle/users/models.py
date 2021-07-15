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

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
