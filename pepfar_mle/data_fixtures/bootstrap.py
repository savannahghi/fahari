"""
Loads data that is grouped by model. Data in the format:
    [
        {
            "model": "setup.paymentterm",
            "records": [
                {
                    "id": "",
                    ....
                },
                {
                    "id": "",
                    "supplier": {
                        "id": ""
                    }
                }
                ...
            ]
        }
        ...
        {
            ...
        }
    ]
"""
import copy
from functools import wraps

from django.apps import apps
from six import string_types

from .common import DataAlreadyExistsException


def model_instance_memo(func):
    """
    Remember the first result and pass it to subsequent calls as the last arg

    This is a single-purpose quick-and-dirty decorator that does not really
    need to be "well-behaved" in the manner enabled by the 'wrapt' package.
    It is TIED IN TO THE IMPLEMENTATION OF _instantiate_model_cls: no reuse.
    """

    class memodict(dict):  # noqa
        __slots__ = ()  # Memory efficiency

    cache = memodict()

    @wraps(func)
    def wrap(*args):
        model_cls = args[0]
        if model_cls in cache:
            # Add object from first invocation, !tuple concatenation!
            args = args + (cache[model_cls],)

        # Always call the wrapped function
        result = func(*args)

        # Add the result to the cache only on the first invocation
        if model_cls not in cache:
            # Save memory by telling Python not to keep an attribute dict
            result.__slots__ = dir(result)
            cache[model_cls] = result

        # Always return the result of the current invocation
        return result

    return wrap


@model_instance_memo
def _instantiate_model_cls(model_cls, field_dict, obj=None):
    """
    A helper method that performs aggressive speed optimizations

    This does some counter-intuitive / un-idiomatic things. It is intentional.
      * the first time we see a model_cls, we remember the obj that it created
      * the next time we see it, we do an obj.copy() then setattr on that

    This bypasses a lot of the Django object instantiation machinery. Our data
    load is largely CPU bound, so this optimization saves time.
    """
    if not obj:
        ret_obj = model_cls(**field_dict)
    else:
        # Bypass lots of Django object instantiation machinery
        ret_obj = copy.copy(obj)
        for field, value in field_dict.items():
            setattr(ret_obj, field, value)

    return ret_obj


def _process_model_spec(model_spec):
    """Save model specs ( JSON file contents ) one at a time

    The following performance-optimization trade-off has been made: THIS
    BOOTSTRAPPER IS OPTIMIZED ONLY FOR CLEAN / COMPLETE DATA LOADS. IF
    YOU CALL IT WHEN THERE IS DATA, IT WILL ABORT.

    That optimization makes it possible to avoid the slowest part of the
    data load process - checking whether each individual record exists.
    The price for that 'idempotency check' was an excruciatingly slow
    load ( an hour to load 11MB on a slow laptop ).

    The caller of this function is expected to catch and handle exceptions.
    ( for readability, this function implements the 'happy path' only ).

    In order to avoid paying a massive performance penalty on lookups, this
    bootstrap enforces a rule that 'other model instances can only be
    referred to by their IDs'. This allows a DB retrieval to be skipped, with
    the bootstrap doing something similar to what is shown below:

        In [21]: p = Person(
            first_name='Juha',
            last_name='Kalulu',
            marital_status=MaritalStatus(id=marital_status_pk),
            gende_id=gender_pk,
            organisation_id=organisation_pk
        )
        In [22]: p.save()

    That approach saves thousands of SQL reads, with a noticeable performance
    impact.

    The dict comprehension that looks like Egyptian hieroglyphics is also part
    of the performance optimizations.
    """
    # Determine the model we are dealing with
    model = model_spec["model"]
    records = model_spec["records"]
    app, model_name = model.split(".", 1)  # split only once
    model_cls = apps.get_model(app_label=app, model_name=model_name)

    # Blow up early when fed crap
    assert isinstance(model, string_types)
    assert isinstance(records, list)
    assert len(records) > 0
    assert isinstance(records[0], dict)
    assert model_cls

    # This is the only 'expensive' check that needs to hit the database
    if model_cls.objects.count() > 0:
        raise DataAlreadyExistsException(
            "{} already has data".format(str(model_cls))
        )  # NOQA

    # Instantiate and bulk create
    # Looks like hieroglyphics...performance optimization with measurable gains
    model_obj_generator = (
        _instantiate_model_cls(
            model_cls,
            {
                field
                if model_cls._meta.get_field(field).get_internal_type()
                not in ["ForeignKey", "OneToOneField"]
                else field + "_id": record[field]  # NOQA
                if model_cls._meta.get_field(field).get_internal_type()
                not in ["ForeignKey", "OneToOneField"]
                else record[field]["id"]  # NOQA
                for field in record.keys()
            },
        )
        for record in records
    )
    model_cls.objects.bulk_create(model_obj_generator)


def process_json(model_specs):
    for model_spec in model_specs:
        _process_model_spec(model_spec)
