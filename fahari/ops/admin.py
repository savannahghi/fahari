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

    list_display = (
        "name",
        "code",
        "description",
        "is_lab_commodity",
        "is_pharmacy_commodity",
    )
    list_filter = (
        "is_lab_commodity",
        "is_pharmacy_commodity",
        "active",
    )


admin.site.register(FacilitySystem, FacilitySystemAdmin)
admin.site.register(FacilitySystemTicket, FacilitySystemTicketAdmin)
admin.site.register(TimeSheet, TimeSheetAdmin)
admin.site.register(Commodity, CommodityAdmin)
