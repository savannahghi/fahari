from django.contrib import admin

from .models import Facility, FacilityAttachment, FacilityUser, Organisation, System


class BaseAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created",
        "created_by",
        "updated",
        "updated_by",
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.pk
            obj.updated_by = request.user.pk

        if change:
            obj.updated_by = request.user.pk

        obj.save()


class FacilityUserInline(admin.TabularInline):
    model = FacilityUser


class FacilityAttachmentInline(admin.TabularInline):
    model = FacilityAttachment


class FacilityAdmin(BaseAdmin):
    inlines = [FacilityUserInline, FacilityAttachmentInline]
    list_display = (
        "name",
        "mfl_code",
        "county",
        "sub_county",
        "constituency",
        "ward",
        "registration_number",
        "keph_level",
    )
    list_filter = (
        "county",
        "operation_status",
        "keph_level",
        "facility_type",
        "owner_type",
    )


class FacilityAttachmentAdmin(BaseAdmin):
    pass


class FacilityUserAdmin(BaseAdmin):
    pass


class OrganisationAdmin(BaseAdmin):
    pass


class SystemAdmin(BaseAdmin):
    pass


admin.site.register(Facility, FacilityAdmin)
admin.site.register(FacilityAttachment, FacilityAttachmentAdmin)
admin.site.register(FacilityUser, FacilityUserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(System, SystemAdmin)
