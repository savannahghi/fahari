"""Base serializers used in the project."""
import logging

from rest_framework import serializers

from .mixins import AuditFieldsMixin

LOGGER = logging.getLogger(__name__)


class BaseSerializer(AuditFieldsMixin):
    """Base class intended for inheritance by 'regular' app serializers."""

    url = serializers.URLField(source="get_absolute_url", read_only=True)

    class Meta:
        datatables_always_serialize = (
            "id",
            "url",
        )
