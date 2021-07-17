from django.contrib import admin

from pepfar_mle.common.admin import BaseAdmin

from .models import FacilitySystem, FacilitySystemTicket, TimeSheet


class FacilitySystemAdmin(BaseAdmin):
    pass


class FacilitySystemTicketAdmin(BaseAdmin):
    pass


class TimeSheetAdmin(BaseAdmin):
    pass


admin.site.register(FacilitySystem, FacilitySystemAdmin)
admin.site.register(FacilitySystemTicket, FacilitySystemTicketAdmin)
admin.site.register(TimeSheet, TimeSheetAdmin)
