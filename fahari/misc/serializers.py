from rest_framework import serializers

from fahari.common.serializers import BaseSerializer

from .models import StockVerificationReceiptsAdapter


class BaseGoogleSheetToDjangoModelAdapterSerializer(BaseSerializer):
    """Base serializer for all Google sheet to Django models adapters."""

    last_ingested = serializers.DateTimeField(format="%d %b %Y, %I:%M:%S %p", read_only=True)


class StockVerificationReceiptsAdapterSerializer(BaseGoogleSheetToDjangoModelAdapterSerializer):
    """Serializer for the `StockVerificationReceiptsAdapter` model."""

    class Meta(BaseSerializer.Meta):
        model = StockVerificationReceiptsAdapter
        fields = "__all__"
        read_only_fields = ("target_model",)
