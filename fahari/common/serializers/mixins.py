"""Shared serializer mixins."""
import logging

from rest_framework import exceptions, serializers
from rest_framework.serializers import ValidationError

from fahari.common.models import Organisation

LOGGER = logging.getLogger(__name__)


def get_organisation(request, initial_data=None):
    """Determine the organisation based on the user and supplied data."""

    user = request.user
    organisation = (
        initial_data.get("organisation")
        if isinstance(initial_data, dict)
        else request.data.get("organisation")
    )

    if organisation:
        try:
            org = Organisation.objects.get(id=organisation)
        except Organisation.DoesNotExist as no_org:
            error = {"organisation": "Ensure the organisation provided exists."}
            raise exceptions.ValidationError(error) from no_org
        return org
    else:
        return user.organisation


class PartialResponseMixin(object):
    """Mixin that allows API clients to specify fields."""

    def strip_fields(self, request, origi_fields):  # noqa
        """
        Select a subset of fields, determined by the `fields` parameter.

        Fetch a subset of fields from the serializer determined by the
        request's ``fields`` query parameter.

        This is an initial implementation that does not handle:
          - nested relationships
          - rejection of unknown fields (currently ignoring unknown fields)
          - wildcards
          - e.t.c
        """
        if request is None or request.method != "GET" or not hasattr(request, "query_params"):
            return origi_fields

        fields = request.query_params.get("fields", None)
        if isinstance(fields, str) and fields:
            fields = [f.strip() for f in fields.split(",")]
            return {field: origi_fields[field] for field in origi_fields if field in fields}
        return origi_fields


class AuditFieldsMixin(PartialResponseMixin, serializers.ModelSerializer):
    """Mixin for organisation, created, updated, created_by and updated_by."""

    def __init__(self, *args, **kwargs):
        """Initialize the mixin by marking the fields it manages as read-only."""

        super().__init__(*args, **kwargs)
        audit_fields = "created", "created_by", "updated", "updated_by", "organisation"
        for field_name in audit_fields:
            if field_name in self.fields:  # pragma: nobranch
                self.fields[field_name].read_only = True

    def populate_audit_fields(self, data, is_create):
        request = self.context["request"]
        user = request.user
        data["updated_by"] = user.pk
        if is_create:
            data["created_by"] = user.pk

            # Do not do this for an Organisation serializer
            # or a model that does not have an organisation attribute
            has_organisation = getattr(self.Meta.model, "organisation", None) is not None
            if self.Meta.model != Organisation and has_organisation:  # pragma: nobranch
                # If an 'organisation' is not explicitly passed in,
                # use the logged in user's organisation, if the request if
                # for creation only
                data["organisation"] = get_organisation(request, self.initial_data)
        return data

    def create(self, validated_data):
        """Ensure that ids are not supplied when creating new instances."""
        initial_data_id = isinstance(self.initial_data, dict) and self.initial_data.get("id")
        if initial_data_id or validated_data.get("id"):
            raise ValidationError({"id": "You are not allowed to pass object with an id"})
        self.populate_audit_fields(validated_data, True)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Ensure that audit fields are set when updating."""
        self.populate_audit_fields(validated_data, False)
        return super().update(instance, validated_data)

    def get_fields(self):
        """Implement support for responses that subset available fields."""
        origi_fields = super().get_fields()
        request = self.context.get("request", None)
        return self.strip_fields(request, origi_fields)
