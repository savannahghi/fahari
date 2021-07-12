from django.contrib import admin

from .models import Facility, FacilityAttachment


class FacilityAdmin(admin.ModelAdmin):
    pass


class FacilityAttachmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Facility, FacilityAdmin)
admin.site.register(FacilityAttachment, FacilityAttachmentAdmin)
