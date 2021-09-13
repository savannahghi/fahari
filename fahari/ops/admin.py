from django.contrib import admin

from fahari.common.admin import BaseAdmin

from .models import (
    Commodity,
    FacilityDevice,
    FacilityDeviceRequest,
    FacilityNetworkStatus,
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


@admin.register(FacilityNetworkStatus)
class FacilityNetworkStatusAdmin(BaseAdmin):

    list_display = (
        "facility",
        "has_network",
        "has_internet",
    )
    list_filter = (
        "facility",
        "has_network",
        "has_internet",
    )


@admin.register(FacilityDevice)
class FacilityDeviceAdmin(BaseAdmin):

    list_display = (
        "facility",
        "number_of_devices",
        "number_of_ups",
        "server_specification",
    )
    list_filter = (
        "facility",
        "number_of_devices",
        "number_of_ups",
    )


@admin.register(FacilityDeviceRequest)
class FacilityDeviceRequestAdmin(BaseAdmin):

    list_display = (
        "facility",
        "device_requested",
        "request_type",
        "request_details",
        "date_requested",
        "delivery_date",
    )
    list_filter = (
        "facility",
        "date_requested",
        "request_type",
    )
