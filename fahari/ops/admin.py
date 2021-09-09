from django.contrib import admin

from fahari.common.admin import BaseAdmin

from .models import (
    Commodity,
    FacilitySystem,
    FacilitySystemTicket,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
)


@admin.register(FacilitySystem)
class FacilitySystemAdmin(BaseAdmin):
    pass


@admin.register(FacilitySystemTicket)
class FacilitySystemTicketAdmin(BaseAdmin):
    pass


@admin.register(TimeSheet)
class TimeSheetAdmin(BaseAdmin):
    pass


@admin.register(Commodity)
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


@admin.register(StockReceiptVerification)
class StockReceiptVerificationAdmin(BaseAdmin):
    pass


@admin.register(UoM)
class UoMAdmin(BaseAdmin):
    pass


@admin.register(UoMCategory)
class UoMCategoryAdmin(BaseAdmin):
    pass
