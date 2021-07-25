from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView, View
from django.views.generic.edit import ModelFormMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .constants import WHITELIST_COUNTIES
from .filters import FacilityFilter, SystemFilter
from .forms import FacilityForm, SystemForm
from .models import Facility, System
from .serializers import FacilitySerializer, SystemSerializer

User = get_user_model()


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


class BaseView(ModelViewSet):
    """Base class for most application views.

    This view's `create` method has been extended to support the creation of
    a single or multiple records.
    """

    def create(self, request, *args, **kwargs):
        """Create and persist single or multiple records."""
        # Check if the data given by the user is composed of a single or
        # multiple records.
        has_many = isinstance(request.data, list)

        # Initialize this viewset's serializer to handle multiple or a single
        # records depending on the value of `has_many` and proceed to create
        # the data.
        serializer = self.get_serializer(data=request.data, many=has_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ApprovedMixin(UserPassesTestMixin, PermissionRequiredMixin, View):
    permission_denied_message = "Permission Denied"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_approved


class HomeView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/home.html"
    permission_required = "users.can_view_dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "dashboard-nav"  # id of active nav element
        return context


class AboutView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/about.html"
    permission_required = "users.can_view_about"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "dashboard-nav"  # id of active nav element
        return context


class FacilityContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "facilities"  # id of selected page
        return context


class FacilityView(FacilityContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/common/facilities.html"
    permission_required = "common.view_facility"


class FacilityCreateView(FacilityContextMixin, BaseFormMixin, CreateView):
    form_class = FacilityForm
    success_url = reverse_lazy("common:facilities")
    model = Facility


class FacilityUpdateView(FacilityContextMixin, UpdateView, BaseFormMixin):
    form_class = FacilityForm
    model = Facility
    success_url = reverse_lazy("common:facilities")


class FacilityDeleteView(FacilityContextMixin, DeleteView, BaseFormMixin):
    form_class = FacilityForm
    model = Facility
    success_url = reverse_lazy("common:facilities")


class FacilityViewSet(BaseView):
    """Facility API view."""

    permissions = {
        "GET": ["common.view_facility"],
        "POST": ["common.add_facility"],
        "PATCH": ["common.change_facility"],
        "DELETE": ["common.delete_facility"],
    }
    queryset = Facility.objects.filter(
        is_fahari_facility=True,
        operation_status="Operational",
        county__in=WHITELIST_COUNTIES,
        active=True,
    )
    serializer_class = FacilitySerializer
    filterset_class = FacilityFilter
    ordering_fields = ("name", "mfl_code", "county", "sub_county", "ward")
    search_fields = (
        "name",
        "mfl_code",
        "registration_number",
    )


class SystemContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "systems"  # id of selected page
        return context


class SystemsView(SystemContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/common/systems.html"
    permission_required = "common.view_system"


class SystemCreateView(SystemContextMixin, BaseFormMixin, CreateView):
    form_class = SystemForm
    success_url = reverse_lazy("common:systems")
    model = System


class SystemUpdateView(SystemContextMixin, UpdateView, BaseFormMixin):
    form_class = SystemForm
    model = System
    success_url = reverse_lazy("common:systems")


class SystemDeleteView(SystemContextMixin, DeleteView, BaseFormMixin):
    form_class = SystemForm
    model = System
    success_url = reverse_lazy("common:systems")


class SystemViewSet(BaseView):
    """System API view."""

    permissions = {
        "GET": ["common.view_system"],
        "POST": ["common.add_system"],
        "PATCH": ["common.change_system"],
        "DELETE": ["common.delete_system"],
    }
    queryset = System.objects.filter(
        active=True,
    )
    serializer_class = SystemSerializer
    filterset_class = SystemFilter
    ordering_fields = ("name",)
    search_fields = ("name",)
