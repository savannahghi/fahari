from django.contrib import admin

from fahari.common.admin import BaseAdmin

from .models import SheetToDBMappingsMetadata, StockVerificationReceiptsAdapter


@admin.register(SheetToDBMappingsMetadata)
class StockToDBMappingsMetadata(BaseAdmin):
    list_display = ("name", "version")


@admin.register(StockVerificationReceiptsAdapter)
class StockVerificationReceiptsAdapterAdmin(BaseAdmin):
    list_display = ("county", "position")
    readonly_fields = BaseAdmin.readonly_fields + ("target_model",)
