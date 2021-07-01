"""A central collection of helper utilities for use in this project."""

import importlib
import random
import string
from decimal import Decimal
from itertools import groupby

import pytz
from dateutil import parser
from django.conf import settings
from django.utils import timezone


def get_utc_localized_datetime(datetime_instance):
    """
    Convert a naive datetime to a UTC localized datetime.

    :datetime_instance datetime A naive datetime instance.
    """
    current_timezone = pytz.timezone(settings.TIME_ZONE)
    localized_datetime = current_timezone.localize(datetime_instance)
    return localized_datetime.astimezone(pytz.utc)


def python_import(module):
    """Import a Python module from a string spec."""
    module_path, attr_name = module.rsplit(".", 1)
    module = importlib.import_module(module_path)
    _attr = getattr(module, attr_name)
    return _attr


def round_off_decimal(value, decimal_places):
    """Round off a decimal value to specified decimal places.

    Args:
    decimal_places (int) Number of decimal places.

    """
    decimal_places_str = "1.{}".format("0" * decimal_places)
    value = Decimal(value)
    return value.quantize(Decimal(decimal_places_str))


def round_off_monetary_value(amount):
    """Round off monetary value to decimal places in set in settings.

    Args:
    amount (string / Decimal) Monetary value to round off.

    """
    return round_off_decimal(Decimal(amount), settings.DECIMAL_PLACES)


def paginate_response(instance, queryset, serializer=None):
    """Get a paginated response given a queryset and current instance."""
    page = instance.paginate_queryset(queryset)
    if serializer is not None:
        serializer = serializer(page, many=True)
    else:
        serializer = instance.get_serializer(page, many=True)
    return instance.get_paginated_response(serializer.data)


def unique_list(list_object):
    """Return a list that contains only unique items."""
    seen = set()
    new_list = []
    for each in list_object:
        if each in seen:
            continue
        new_list.append(each)
        seen.add(each)

    return new_list


def get_bool_from_string(value):
    """Cast a string passed to a Boolean.

    For a true boolean value, the string passed("values") has to either be
    'true', 'yes' or 'y'. Otherwise, a False boolean value is returned
    """
    value = str(value)
    allowed_values = ("true", "yes", "y")
    if value.lower() in allowed_values:
        return True
    return False


# Not used but Required when running migrations
def random_string_generator(size=6):
    """Generate a random uppercase string of any size."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for each in range(size))


# Not used but Required when running migrations
def generate_batch_number():
    """Generate a batch number if one is not provided.

    Auto-generated batch numbers will have the format
    yymmdd-hhmmss-{5 random chars}.
    """
    return "BN-{datetime}-{random}".format(
        datetime=timezone.now().strftime("%y%m%d-%H%M%S"),
        random=random_string_generator(size=5),
    )


def string_date_to_datetime(date_to_format):
    """Format string dates into datetime objects.

    ``parser.parse`` is timezone aware unlike ``datetime.strptime``

    Outputs for both scenarios:
        1. parser.parse('2016-10-10T10:34:23.434543Z')
        >>> datetime.datetime(
                        2016, 10, 10, 10, 34, 23, 434543, tzinfo=tzutc())

        2. datetime.strptime('2016-10-10T10:34:23.434543Z',
                             '%Y-%m-%dT%H:%M:%S.%fZ')
        >>> datetime.datetime(2016, 8, 24, 20, 6, 20, 403726)

    In cases where we need to do date addition or subtraction, we cannot
    do the math when one value is timezone aware while the other is
    timezone naive.
    """
    return parser.parse(date_to_format) if date_to_format else None


def aggregate_items(aggregation_key, data):
    """Aggregate items by the 'aggregation_key'."""
    products = []
    sorted_products = sorted(data, key=lambda y: y[aggregation_key])
    grouped_data = groupby(sorted_products, key=lambda x: x[aggregation_key])
    for k, g in grouped_data:
        products.append({"id": str(k), "product_list": list(g)})
    return products
