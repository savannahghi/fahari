from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.utils import timezone
from django.views.generic import View
from django.views.generic.edit import ModelFormMixin

User = get_user_model()


class ApprovedMixin(UserPassesTestMixin, PermissionRequiredMixin, View):
    permission_denied_message = "Permission Denied"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_approved


class BaseFormMixin(ModelFormMixin, View):
    def form_valid(self, form):
        user = self.request.user
        instance = form.instance
        instance.updated_by = user.pk
        instance.updated = timezone.now()

        if instance.created_by is None:  # pragma: nobranch
            instance.created_by = user.pk

        if (
            getattr(instance, "organisation", None) is None
            and isinstance(user, User)
            and getattr(user, "organisation", None) is not None
        ):
            instance.organisation = user.organisation
        return super().form_valid(form)


class FormContextMixin(ModelFormMixin, LoginRequiredMixin, View):
    """Mixin to inject context data into a form."""

    def get_form_context(self) -> Dict[str, Any]:
        """Return the data to be used as a form's context."""

        return {
            "view": self,
            "args": getattr(self, "args", ()),
            "kwargs": getattr(self, "kwargs", {}),
            "request": getattr(self, "request", None),
        }

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Extend the base implementation to add context data on the returned form kwargs."""

        kwargs = super().get_form_kwargs()
        kwargs["context"] = self.get_form_context()
        return kwargs
