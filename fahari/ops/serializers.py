from rest_framework import serializers

from fahari.common.serializers import BaseSerializer

from .models import FacilitySystem, FacilitySystemTicket


class FacilitySystemSerializer(BaseSerializer):

    url = serializers.URLField(source="get_absolute_url", read_only=True)
    facility_name = serializers.ReadOnlyField()
    system_name = serializers.ReadOnlyField()

    class Meta(BaseSerializer.Meta):
        model = FacilitySystem
        fields = "__all__"


class FacilitySystemTicketSerializer(BaseSerializer):

    url = serializers.URLField(source="get_absolute_url", read_only=True)
    facility_system_name = serializers.ReadOnlyField()
    is_open = serializers.ReadOnlyField()

    class Meta(BaseSerializer.Meta):
        model = FacilitySystemTicket
        fields = "__all__"
