"""Common serializers."""
import logging

from rest_framework import serializers

from ..models import Facility, System, UserFacilityAllotment
from .base_serializers import BaseSerializer

LOGGER = logging.getLogger(__name__)


class FacilitySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Facility
        fields = "__all__"


class SystemSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = System
        fields = "__all__"


class UserFacilityAllotmentSerializer(BaseSerializer):

    user_name = serializers.ReadOnlyField(source="user.username")
    allotment_type_name = serializers.ReadOnlyField(source="get_allotment_type_display")

    class Meta(BaseSerializer.Meta):
        model = UserFacilityAllotment
        fields = "__all__"
