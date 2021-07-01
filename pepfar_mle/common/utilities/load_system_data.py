"""Utilities to load system data from JSON boostrap files."""
import glob
import itertools
import uuid
from collections import OrderedDict

from django.apps import apps
from django.forms import DurationField as DurationFieldForm

from pepfar_mle.data_fixtures.bootstrap_flat import bulk_create, empty_generator
from pepfar_mle.data_fixtures.common import process_json_files

model_classes = OrderedDict([])


def get_related(field_instance, value, organisation):
    """Get related model instance."""
    is_org_model = field_instance.related_model._meta.model_name != "organisation"
    value.update(
        {"organisation": organisation}
    ) if organisation and is_org_model else None
    return field_instance.related_model.objects.get(**value)


def get_value(model_cls, field, value, organisation):
    """Get field instance value."""
    field_instance = model_cls._meta.get_field(field)

    field_type = field_instance.get_internal_type()

    if field_type == "DurationField":
        return DurationFieldForm().to_python(value)

    if field_type not in ["ForeignKey", "OneToOneField"]:
        return value

    field_instance.model._meta.get_field("organisation")
    bulk_create(model_classes)
    return get_related(field_instance, value, organisation)


def get_object(model_cls, record):
    """Instantiate a model instance with data supplied as the record dict."""
    attrs = {
        field: get_value(model_cls, field, record[field], record["organisation"]["id"])
        for field in record.keys()
    }
    model_obj = model_cls(**attrs)
    return model_obj


def generate_records(records, strict_mode=False):
    """Instantiate records as model classes."""
    for record in records:
        model_name = record.pop("model")
        model_cls = apps.get_model(model_name)
        if model_cls not in model_classes.keys():
            model_classes.setdefault(model_cls, empty_generator())
            # load data already generated for other model clases before
            # going ahead to generate for next model
            bulk_create(model_classes)

        model_obj = get_object(model_cls, record)
        model_classes[model_cls] = itertools.chain(
            model_classes[model_cls], [model_obj]
        )

    return model_classes


def process_json(records, organisation, user, *args, **kwargs):
    """
    Load from JSON.

    Override `data_fixtures.bootstrap_flat.process_json`
    to allow passing `organisation`, `created_by` and
    `updated_by` attributes.
    """
    for each in records:
        each.update(
            {
                "organisation": {"id": organisation},
                "created_by": user,
                "updated_by": user,
                "id": uuid.uuid4(),
            }
        )
    objects = generate_records(records, *args, **kwargs)
    bulk_create(objects)


def load_system_data(data_files, organisation, user):
    """Load system data using the supplied organisation and user."""
    process_json_files(
        sorted(glob.glob(data_files)),
        process_json,
        organisation=organisation,
        user=user,
        strict_mode=False,
    )
