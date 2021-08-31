from functools import lru_cache
from itertools import chain
from typing import Collection, Dict, Iterable, Optional, Tuple, cast

from ..constants import ADMINISTRATIVE_UNITS

FieldChoice = Tuple[str, str]

_CONSTITUENCIES = "Constituencies"
_SUB_COUNTIES = "Sub Counties"


def _sorted_field_choices(choices: Iterable[FieldChoice]) -> Collection[FieldChoice]:
    # Sort by the display value rather than the storage value. This way, the choices
    # appear sorted on the select DOM component of the user interface.
    sorted_choices = sorted(choices, key=lambda choice: choice[1])
    return tuple(sorted_choices)


@lru_cache(maxsize=None)
def get_counties() -> Collection[FieldChoice]:
    """Return a `Collection` of choices the counties involved in the Fahari ya Jamii Project.

    :return: A Collection of choices of the counties involved in the Fahari ya
             Jamii Project.
    """
    return tuple((county, county) for county in ADMINISTRATIVE_UNITS)


@lru_cache(maxsize=None)
def get_constituencies() -> Collection[FieldChoice]:
    """Return a `Collection` of choices of the constituencies involved in the Fahari ya Jamii Project.

    :return: A Collection of choices of the constituencies involved in the
             Fahari ya Jamii Project.
    """
    constituencies = (get_constituencies_for_county(county[0]) for county in get_counties())
    return _sorted_field_choices(chain.from_iterable(constituencies))


@lru_cache(maxsize=None)
def get_constituencies_for_county(county: str) -> Collection[FieldChoice]:
    """Return a `Collection` of choices of the constituencies of the given county.

    If the given county doesn't exist, an empty `Collection` will be returned
    instead.

    :param county: The county whose constituencies to return.

    :return: A Collection of choices of the constituencies that belong to the
             given county or an empty Collection if the provided county doesn't
             exist.
    """
    county_admin_units = ADMINISTRATIVE_UNITS.get(county, dict())
    constituencies = county_admin_units.get(_CONSTITUENCIES, tuple())
    return _sorted_field_choices((constituency, constituency) for constituency in constituencies)


@lru_cache(maxsize=None)
def get_sub_counties() -> Collection[FieldChoice]:
    """Return a `Collection` of choices of all the sub-counties in the Fahari ya Jamii Project.

    :return: A Collection of choices of all the sub-counties involved in the
             Fahari ya Jamii Project.
    """
    sub_counties = (get_sub_counties_for_county(county[0]) for county in get_counties())
    return _sorted_field_choices(chain.from_iterable(sub_counties))


@lru_cache(maxsize=None)
def get_sub_counties_for_county(county: str) -> Collection[FieldChoice]:
    """Return a `Collection` of choices of the sub-counties of the given county.

    If the given county doesn't exist, an empty `Collection` will be returned
    instead.

    :param county: The county whose sub-counties to return.

    :return: An Collection of choices of the sub-counties that belong to the
             given county or an empty Collection if the provided county doesn't
             exist.
    """
    county_admin_units = ADMINISTRATIVE_UNITS.get(county, dict())
    sub_counties = county_admin_units.get(_SUB_COUNTIES, dict())
    return _sorted_field_choices((sub_county, sub_county) for sub_county in sub_counties)


@lru_cache(maxsize=None)
def get_wards() -> Collection[FieldChoice]:
    """Return a `Collection` of choices of the wards involved in the Fahari ya Jamii Project.

    :return: A Collection of choices of the wards involved in the Fahari ya
             Jamii Project.
    """
    wards = (get_wards_for_sub_county(sub_county[0]) for sub_county in get_sub_counties())
    return _sorted_field_choices(chain.from_iterable(wards))


@lru_cache(maxsize=None)
def get_wards_for_sub_county(sub_county: str) -> Collection[FieldChoice]:
    """Return a `Collection` of choices of the wards of the given sub-county.

    If the given sub-county doesn't exist, an empty `Collection` will be
    returned.

    :param sub_county: The sub-county whose wards to return.

    :return: A Collection of choices of the wards that belong to the given
             sub-county or an empty Collection if the provided sub-county
             doesn't exist.
    """
    owning_county: Optional[str] = None
    for county in get_counties():
        if (sub_county, sub_county) in get_sub_counties_for_county(county[0]):
            owning_county = county[0]
            break

    if owning_county is None:
        return tuple()

    sub_counties = cast(
        Dict[str, Collection[str]], ADMINISTRATIVE_UNITS[owning_county][_SUB_COUNTIES]
    )
    wards = sub_counties[sub_county]
    return _sorted_field_choices((ward, ward) for ward in wards)


def has_constituency(county: str, constituency: str) -> bool:
    """Check if the given constituency exists in the given county.

    The provided county MUST be part of the Fahari ya Jamii program, otherwise,
    a `ValueError` will be raised.

    Return `true` if the given constituency exists and belongs to the given
    county or `false` otherwise.

    :param county: A county in the FYJ program.
    :param constituency: The constituency whose ownership we want to check.

    :return: true if the given constituency belongs to the given county or
             false otherwise.

    :raise ValueError: If the given county is not part of the FYJ program.
    """
    if county not in ADMINISTRATIVE_UNITS:
        raise ValueError('county "{}" does not exist'.format(county))
    return (constituency, constituency) in get_constituencies_for_county(county)


def has_sub_county(county: str, sub_county: str) -> bool:
    """Check if the given sub-county exists in the given county.

    The provided county MUST be part of the Fahari ya Jamii program, otherwise,
    a `ValueError` will be raised.

    Return `true` if the given sub-county exists and belongs to the given
    county or `false` otherwise.

    :param county: A county in the FYJ program.
    :param sub_county: The sub-county whose ownership we want to check.

    :return: true if the given sub-county belongs to the given county or false
             otherwise.

    :raise ValueError: If the given county is not part of the FYJ program.
    """
    if county not in ADMINISTRATIVE_UNITS:
        raise ValueError('county "{}" does not exist'.format(county))
    return (sub_county, sub_county) in get_sub_counties_for_county(county)


def has_ward(sub_county: str, ward: str) -> bool:
    """Check if the given ward exists inn the given sub-county.

    The provided sub-county MUST belong to a sub-county in thr Fahari ya Jamii
    program, otherwise, a `ValueError` will be raised.

    Return `true` if the given ward exists and belongs to the given sub-county
    or `false` otherwise.

    :param sub_county: A sub-county belonging to a county in the FYJ program.
    :param ward: The ward whose ownership we want to check.

    :return: true if the given ward belongs to the given sub-county or false
             otherwise.

    :raise ValueError: If the given sub-county doesn't belong to a county in
           the FYJ program.
    """
    if (sub_county, sub_county) not in get_sub_counties():
        raise ValueError('sub county "{}" does not exist'.format(sub_county))
    return (ward, ward) in get_wards_for_sub_county(sub_county)
