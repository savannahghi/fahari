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

from .dashboard import (
    get_active_facility_count,
    get_active_user_count,
    get_appointments_mtd,
    get_fahari_facilities_queryset,
    get_open_ticket_count,
)
from .filters import FacilityFilter, FacilityUserFilter, SystemFilter, UserFacilityAllotmentFilter
from .forms import FacilityForm, FacilityUserForm, SystemForm, UserFacilityAllotmentForm
from .models import Facility, FacilityUser, System, UserFacilityAllotment
from .serializers import (
    FacilitySerializer,
    FacilityUserSerializer,
    SystemSerializer,
    UserFacilityAllotmentSerializer,
)

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


class GetKwargsMixin(ModelFormMixin, LoginRequiredMixin, View):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


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
        context["selected"] = "dashboard"  # id of selected page

        # dashboard summaries
        user = self.request.user
        context["active_facility_count"] = get_active_facility_count(user)
        context["open_ticket_count"] = get_open_ticket_count(user)
        context["user_count"] = get_active_user_count(user)
        context["appointments_mtd"] = get_appointments_mtd(user)
        return context


class AboutView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/about.html"
    permission_required = "users.can_view_about"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active"] = "dashboard-nav"  # id of active nav element
        context["selected"] = "dashboard"  # id of selected page
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
    queryset = get_fahari_facilities_queryset()
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
    queryset = System.objects.filter(
        active=True,
    )
    serializer_class = SystemSerializer
    filterset_class = SystemFilter
    ordering_fields = ("name",)
    search_fields = ("name",)


class FacilityUserContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "facility-users"  # id of selected page
        return context


class FacilityUserView(FacilityUserContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView):
    template_name = "pages/common/facility_users.html"
    permission_required = "common.view_facilityuser"


class FacilityUserCreateView(SystemContextMixin, BaseFormMixin, CreateView):
    form_class = FacilityUserForm
    model = FacilityUser
    success_url = reverse_lazy("common:facility_users")


class FacilityUserUpdateView(SystemContextMixin, UpdateView, BaseFormMixin):
    form_class = FacilityUserForm
    model = FacilityUser
    success_url = reverse_lazy("common:facility_users")


class FacilityUserDeleteView(SystemContextMixin, DeleteView, BaseFormMixin):
    form_class = FacilityUserForm
    model = FacilityUser
    success_url = reverse_lazy("common:facility_users")


class FacilityUserViewSet(BaseView):
    queryset = FacilityUser.objects.filter(
        active=True,
    )
    serializer_class = FacilityUserSerializer
    filterset_class = FacilityUserFilter
    ordering_fields = (
        "facility__name",
        "user__name",
    )
    search_fields = (
        "facility__name",
        "user__name",
    )


class UserFacilityAllotmentContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["selected"] = "user-facility-allotments"  # id of selected page
        return context


class UserFacilityAllotmentView(
    UserFacilityAllotmentContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    template_name = "pages/common/user_facility_allotments.html"
    permission_required = "common.view_userfacilityallotment"


class UserFacilityAllotmentCreateView(
    UserFacilityAllotmentContextMixin, BaseFormMixin, CreateView
):
    form_class = UserFacilityAllotmentForm
    model = UserFacilityAllotment
    success_url = reverse_lazy("common:user_facility_allotments")


class UserFacilityAllotmentUpdateView(
    UserFacilityAllotmentContextMixin, BaseFormMixin, UpdateView
):
    form_class = UserFacilityAllotmentForm
    model = UserFacilityAllotment
    success_url = reverse_lazy("common:user_facility_allotments")


class UserFacilityAllotmentDeleteView(
    UserFacilityAllotmentContextMixin, BaseFormMixin, DeleteView
):
    form_class = UserFacilityAllotmentForm
    model = UserFacilityAllotment
    success_url = reverse_lazy("common:user_facility_allotments")


class UserFacilityViewSet(BaseView):
    queryset = UserFacilityAllotment.objects.filter(active=True)
    serializer_class = UserFacilityAllotmentSerializer
    filterset_class = UserFacilityAllotmentFilter
    ordering_fields = ("user__name", "allotment_type")
    search_fields = ("allotment_type", "user__name")
