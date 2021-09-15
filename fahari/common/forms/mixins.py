from typing import Any, Dict, Optional, Union

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.forms import ModelForm

from ..models import Facility, UserFacilityAllotment
from ..models.common_models import FacilityManager, FacilityQuerySet

User = get_user_model()


class FormContextMixin(ModelForm):
    """Add context to a form."""

    def __init__(self, *args, **kwargs):
        self._context: Dict[str, Any] = kwargs.pop("context", {})
        super().__init__(*args, **kwargs)

    @property
    def context(self) -> Dict[str, Any]:
        """Return the context as passed on the form during initialization."""

        return self._context


class GetUserFromContextMixin(FormContextMixin):
    """Add a method to retrieve the logged in user from a form's context."""

    def get_logged_in_user(self) -> Optional[Model]:
        """Determine and return the logged in user from the context."""

        request = self.context.get("request", None)
        user = getattr(request, "user", None) if request else None
        return user


class GetAllottedFacilitiesMixin(GetUserFromContextMixin):
    """Add a method to retrieve the allotted facilities for the logged-in user.

    The logged-in user is determined from a form's context data.
    """

    def get_allotted_facilities(self) -> Union[FacilityManager, FacilityQuerySet]:
        """Return a queryset consisting of all the allotted facilities of the logged in user.

        If the logged in user cannot be determined, then an empty queryset is returned instead.
        """

        user = self.get_logged_in_user()
        if not user:
            return Facility.objects.none()
        return UserFacilityAllotment.get_facilities_for_user(user)
