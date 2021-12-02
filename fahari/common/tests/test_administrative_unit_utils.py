import pytest

from fahari.common.utils import (
    get_constituencies,
    get_constituencies_for_county,
    get_counties,
    get_sub_counties,
    get_sub_counties_for_county,
    get_wards,
    get_wards_for_sub_county,
    has_constituency,
    has_sub_county,
    has_ward,
)


def test_get_counties():
    counties = get_counties()
    assert ("Nairobi", "Nairobi") in counties
    assert ("Kajiado", "Kajiado") in counties


def test_get_constituencies():
    constituencies = get_constituencies()
    assert ("Magadi", "Magadi") in constituencies
    assert ("Kibra", "Kibra") in constituencies
    assert ("Dagoretti North", "Dagoretti North") in constituencies
    assert ("Kajiado East", "Kajiado East") in constituencies
    assert ("Starehe", "Starehe") in constituencies
    assert len(constituencies) == 23


def test_get_constituencies_for_county():
    constituencies = get_constituencies_for_county("Kajiado")
    assert ("Magadi", "Magadi") in constituencies
    assert ("Kajiado Central", "Kajiado Central") in constituencies
    assert ("Kajiado East", "Kajiado East") in constituencies
    assert ("Kajiado South", "Kajiado South") in constituencies
    assert len(constituencies) == 6


def test_get_constituencies_for_county_with_missing_county():
    """Assert correct output when a non existing county is given as input."""
    constituencies = get_constituencies_for_county("Marsabit")
    assert len(constituencies) == 0


def test_get_sub_counties():
    sub_counties = get_sub_counties()
    assert ("Loitokitok", "Loitokitok") in sub_counties
    assert ("Roysambu", "Roysambu") in sub_counties
    assert ("Kibra", "Kibra") in sub_counties
    assert ("Dagoretti South", "Dagoretti South") in sub_counties
    assert len(sub_counties) == 22


def test_get_sub_counties_for_county():
    sub_counties = get_sub_counties_for_county("Nairobi")
    assert ("Westlands", "Westlands") in sub_counties
    assert len(sub_counties) == 17


def test_get_sub_counties_for_county_with_missing_county():
    """Assert correct output when a non existing county is given as input."""
    sub_counties = get_sub_counties_for_county("Mombasa")
    assert len(sub_counties) == 0


def test_get_wards_for_sub_county():
    wards = get_wards_for_sub_county("Dagoretti North")
    assert ("Kilimani", "Kilimani") in wards
    assert len(wards) == 5


def test_get_wards():
    wards = get_wards()
    assert ("Ongata Rongai", "Ongata Rongai") in wards
    assert ("Ewuaso Oo Nkidong'i", "Ewuaso Oo Nkidong'i") in wards
    assert ("Iloodokilani", "Iloodokilani") in wards
    assert ("Keekonyokie", "Keekonyokie") in wards
    assert ("Magadi", "Magadi") in wards
    assert ("Mosiro", "Mosiro") in wards
    assert ("Ziwani/Kariokor", "Ziwani/Kariokor") in wards
    assert ("Landimawe", "Landimawe") in wards
    assert ("Nairobi South", "Nairobi South") in wards
    assert len(wards) == 110


def test_get_wards_for_sub_county_with_missing_sub_county():
    """Assert correct output when a non-existing sub-county is given as input."""
    wards = get_wards_for_sub_county("Naivasha")
    assert len(wards) == 0


def test_has_constituency():
    assert has_constituency("Kajiado", "Magadi")
    assert has_constituency("Nairobi", "Starehe")
    assert not has_constituency("Nairobi", "Kajiado East")


def test_has_constituency_with_missing_county():
    with pytest.raises(ValueError):
        has_constituency("Mombasa", "Lamu")


def test_has_sub_county():
    assert has_sub_county("Nairobi", "Dagoretti North")
    assert not has_sub_county("Kajiado", "Westlands")


def test_has_sub_county_with_missing_county():
    with pytest.raises(ValueError):
        has_sub_county("Nakuru", "Naivasha")


def test_has_wards():
    assert has_ward("Ruaraka", "Korogocho")
    assert has_ward("Mathare", "Huruma")
    assert has_ward("Kajiado Central", "Ildamat")
    assert has_ward("Kajiado North", "Ngong")
    assert not has_ward("Kajiado East", "Ngei")


def test_has_ward_with_missing_sub_county():
    with pytest.raises(ValueError):
        assert has_ward("Kitui", "Kitui")
