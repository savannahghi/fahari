from django.contrib import admin

from .models import Facility, FacilityAttachment, Organisation, System


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


class FacilityAdmin(BaseAdmin):
    pass


class FacilityAttachmentAdmin(BaseAdmin):
    pass


class OrganisationAdmin(BaseAdmin):
    pass


class SystemAdmin(BaseAdmin):
    pass


admin.site.register(Facility, FacilityAdmin)
admin.site.register(FacilityAttachment, FacilityAttachmentAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(System, SystemAdmin)
