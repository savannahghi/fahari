"""Shared serializer mixins."""
import logging

from rest_framework import serializers

from .mixins import AuditFieldsMixin
from .models import Facility, FacilityUser, System

LOGGER = logging.getLogger(__name__)


class BaseSerializer(AuditFieldsMixin):
    """Base class intended for inheritance by 'regular' app serializers."""

    url = serializers.URLField(source="get_absolute_url", read_only=True)

    class Meta:
        datatables_always_serialize = (
            "id",
            "url",
        )


class FacilitySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Facility
        fields = "__all__"


class SystemSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = System
        fields = "__all__"


class FacilityUserSerializer(BaseSerializer):

    facility_name = serializers.ReadOnlyField(source="facility.name")
    user_name = serializers.ReadOnlyField(source="user.name")

    class Meta(BaseSerializer.Meta):
        model = FacilityUser
        fields = "__all__"