from django.contrib import admin

from .models import Facility, FacilityAttachment, Organisation


class FacilityAdmin(admin.ModelAdmin):
    pass


class FacilityAttachmentAdmin(admin.ModelAdmin):
    pass


class OrganisationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Facility, FacilityAdmin)
admin.site.register(FacilityAttachment, FacilityAttachmentAdmin)
admin.site.register(Organisation, OrganisationAdmin)
