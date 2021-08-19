from django.contrib import admin

from fahari.common.admin import BaseAdmin

from .models import Commodity, FacilitySystem, FacilitySystemTicket, TimeSheet


class FacilitySystemAdmin(BaseAdmin):
    pass


class FacilitySystemTicketAdmin(BaseAdmin):
    pass


class TimeSheetAdmin(BaseAdmin):
    pass


class CommodityAdmin(BaseAdmin):
    pass


admin.site.register(FacilitySystem, FacilitySystemAdmin)
admin.site.register(FacilitySystemTicket, FacilitySystemTicketAdmin)
admin.site.register(TimeSheet, TimeSheetAdmin)
admin.site.register(Commodity, CommodityAdmin)
