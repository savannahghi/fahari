from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from fahari.common.dashboard import (
    get_active_facility_count,
    get_active_user_count,
    get_appointments_mtd,
    get_open_ticket_count,
)
from fahari.common.forms import FacilityForm, SystemForm, UserFacilityAllotmentForm
from fahari.common.models import Facility, System, UserFacilityAllotment

from ..mixins import ApprovedMixin, BaseFormMixin


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
        context["available_fields_url"] = reverse_lazy("api:facility-get-available-fields")
        context["dump_data_url"] = reverse_lazy("api:facility-dump-data")
        context["get_filter_form_url"] = reverse_lazy("api:facility-get-filter-form")
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


class SystemContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # type: ignore
        context["active"] = "facilities-nav"  # id of active nav element
        context["available_fields_url"] = reverse_lazy("api:system-get-available-fields")
        context["dump_data_url"] = reverse_lazy("api:system-dump-data")
        context["get_filter_form_url"] = reverse_lazy("api:system-get-filter-form")
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
