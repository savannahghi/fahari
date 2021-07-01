"""
Loads data that is not grouped by model; hence more flattened layout.

Data in the format:
    [
        {
            "model": "setup.paymentterm",
            "id": "",
            ....
        },
        {
            "model": "documents.purchasesinvoice",
            "id": "",
            "supplier": {
                "id": ""
            }
        }
    ]

App dependency should be observed so that records that are depended upon by
others are loaded prior to loading the depending records.
"""
import itertools
import logging
from collections import OrderedDict

from data_fixtures.common import DataAlreadyExistsException
from django.apps import apps

LOGGER = logging.getLogger(__name__)


def empty_generator():
    return iter(())


def has_records(model_cls, **kwargs):
    return model_cls.objects.filter(**kwargs).exists()


def bulk_create(objects):
    for model_cls, objects in objects.items():
        model_cls.objects.bulk_create(objects)


def generate_records(records, strict_mode=False):
    model_clses = OrderedDict([])
    for record in records:
        model_name = record.pop("model")
        model_cls = apps.get_model(model_name)
        if model_cls not in model_clses.keys():
            LOGGER.debug("bulk loading {}".format(model_cls))
            model_clses.setdefault(model_cls, empty_generator())
            # load data already generated for other model clases before
            # going ahead to generate for next model
            bulk_create(model_clses)
            if strict_mode and has_records(model_cls):
                raise DataAlreadyExistsException(
                    "{} already has data".format(str(model_cls))
                )

        attrs = {
            field
            if model_cls._meta.get_field(field).get_internal_type()
            not in ["ForeignKey", "OneToOneField"]
            else field + "_id": record[field]  # NOQA
            if model_cls._meta.get_field(field).get_internal_type()
            not in ["ForeignKey", "OneToOneField"]
            else record[field]["id"]  # NOQA
            for field in record.keys()
        }
        model_obj = model_cls(**attrs)
        model_clses[model_cls] = itertools.chain(model_clses[model_cls], [model_obj])

    return model_clses


def process_json(records, *args, **kwargs):
    objects = generate_records(records, *args, **kwargs)
    bulk_create(objects)
