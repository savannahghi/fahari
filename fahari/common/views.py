from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.views.generic import TemplateView, View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from fahari.common.filters import FacilityFilter

from .constants import WHITELIST_COUNTIES
from .models import Facility
from .serializers import FacilitySerializer


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


class FacilityView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/common/facilities.html"
    permission_required = "common.view_facility"

    # TODO Actions...add
    # TODO Edit other page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "facilities"  # id of selected page
        return context


class SystemsView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/common/systems.html"
    permission_required = "common.view_system"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "systems"  # id of selected page
        return context


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
    )
    serializer_class = FacilitySerializer
    filterset_class = FacilityFilter
    ordering_fields = ("name", "mfl_code", "county", "sub_county", "ward")
    search_fields = (
        "name",
        "mfl_code",
        "registration_number",
    )
