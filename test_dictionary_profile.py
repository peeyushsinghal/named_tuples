"""
Test module for dictionary_profile.py functions.
Contains test cases for profile data analysis functions including blood type, location, and age calculations.
"""

import pytest
from decimal import Decimal
import datetime
from dictionary_profile import (
    get_largest_blood_type_dict,
    get_mean_current_location_dict,
    get_oldest_person_age_dict,
    get_average_age_dict,
)


@pytest.fixture
def sample_profiles():
    """
    Fixture providing sample profile data for testing.

    Returns:
        List[Dict]: A list of three profile dictionaries with test data:
            - John Doe from NYC (A+ blood type, born 1990)
            - Jane Smith from LA (B- blood type, born 1985)
            - Bob Wilson from London (A+ blood type, born 1995)
    """
    return [
        {
            "blood_group": "A+",
            "current_location": (
                Decimal("40.7128"),
                Decimal("-74.0060"),
            ),  # NYC coordinates
            "birthdate": datetime.datetime(1990, 1, 1),
            "name": "John Doe",
            "sex": "M",
            "address": "123 Main St",
            "mail": "john@example.com",
            "username": "johnd",
            "job": "Engineer",
            "company": "Tech Corp",
            "ssn": "123-45-6789",
            "residence": "456 Home St",
            "website": "www.john.com",
        },
        {
            "blood_group": "B-",
            "current_location": (
                Decimal("34.0522"),
                Decimal("-118.2437"),
            ),  # LA coordinates
            "birthdate": datetime.datetime(1985, 6, 15),
            "name": "Jane Smith",
            "sex": "F",
            "address": "789 Oak St",
            "mail": "jane@example.com",
            "username": "janes",
            "job": "Designer",
            "company": "Design Co",
            "ssn": "987-65-4321",
            "residence": "321 House St",
            "website": "www.jane.com",
        },
        {
            "blood_group": "A+",
            "current_location": (
                Decimal("51.5074"),
                Decimal("-0.1278"),
            ),  # London coordinates
            "birthdate": datetime.datetime(1995, 12, 31),
            "name": "Bob Wilson",
            "sex": "M",
            "address": "10 Park Lane",
            "mail": "bob@example.com",
            "username": "bobw",
            "job": "Manager",
            "company": "Manage Ltd",
            "ssn": "456-78-9012",
            "residence": "15 Home Ave",
            "website": "www.bob.com",
        },
    ]


def test_get_largest_blood_type_dict(sample_profiles):
    """
    Test get_largest_blood_type_dict function with sample profiles.

    Verifies that:
        - Function correctly identifies 'A+' as most common blood type
        - Returns result as a single-element set
    """
    result = get_largest_blood_type_dict(sample_profiles)
    assert result == {"A+"}, "Should return {'A+'} as it appears twice"


def test_get_mean_current_location_dict(sample_profiles):
    """
    Test get_mean_current_location_dict function with sample profiles.

    Verifies that:
        - Function correctly calculates average latitude and longitude
        - Result is within 0.01 decimal degrees of expected values
        - Returns coordinates as Decimal values for precision
    """
    result = get_mean_current_location_dict(sample_profiles)
    assert (
        abs(result[0] - Decimal("42.0908")) < 0.01
    ), "Latitude should be approximately equal"
    assert (
        abs(result[1] - Decimal("-64.1258")) < 0.01
    ), "Longitude should be approximately equal"


def test_get_oldest_person_age_dict(sample_profiles):
    """
    Test get_oldest_person_age_dict function with sample profiles.

    Verifies that:
        - Function correctly identifies oldest person (Jane, born 1985)
        - Returns correct age based on current year
    """
    current_year = datetime.datetime.now().year
    result = get_oldest_person_age_dict(sample_profiles)
    expected = current_year - 1985  # Jane's birth year
    assert result == expected, f"Should return {expected} years"


def test_get_average_age_dict(sample_profiles):
    """
    Test get_average_age_dict function with sample profiles.

    Verifies that:
        - Function correctly calculates mean age of all profiles
        - Result is within 0.01 years of expected value
    """
    current_year = datetime.datetime.now().year
    result = get_average_age_dict(sample_profiles)
    expected = (current_year - 1990 + current_year - 1985 + current_year - 1995) / 3
    assert abs(result - expected) < 0.01, "Average age should be approximately equal"


def test_empty_profiles():
    """
    Test all functions with empty profile list.

    Verifies that:
        - All functions raise ValueError when given empty list
        - Error handling is consistent across all functions
    """
    empty_profiles = []
    with pytest.raises(ValueError):
        get_largest_blood_type_dict(empty_profiles)
    with pytest.raises(ValueError):
        get_mean_current_location_dict(empty_profiles)
    with pytest.raises(ValueError):
        get_oldest_person_age_dict(empty_profiles)
    with pytest.raises(ValueError):
        get_average_age_dict(empty_profiles)


def test_single_profile(sample_profiles):
    """
    Test all functions with single profile.

    Verifies that:
        - Functions work correctly with single-element list
        - Results match expected values for John's profile
    """
    single_profile = [sample_profiles[0]]
    assert get_largest_blood_type_dict(single_profile) == {"A+"}
    assert get_mean_current_location_dict(single_profile) == (
        Decimal("40.7128"),
        Decimal("-74.0060"),
    )
    assert (
        get_oldest_person_age_dict(single_profile)
        == datetime.datetime.now().year - 1990
    )
    assert get_average_age_dict(single_profile) == datetime.datetime.now().year - 1990


def test_duplicate_profiles(sample_profiles):
    """
    Test functions with duplicated profile data.

    Verifies that:
        - Functions handle duplicate data correctly
        - Most common blood type remains 'A+' when profiles are duplicated
    """
    duplicates = sample_profiles + sample_profiles
    result = get_largest_blood_type_dict(duplicates)
    assert result == {"A+"}, "Should still return {'A+'} with duplicated profiles"


def test_different_locations():
    """
    Test location calculation with extreme coordinates.

    Verifies that:
        - Function correctly averages extreme latitude/longitude values
        - North Pole (90, 180) and South Pole (-90, -180) average to (0, 0)
    """
    profiles = [
        {
            "blood_group": "A+",
            "current_location": (90, 180),  # North Pole
            "birthdate": datetime.datetime(1990, 1, 1),
            "name": "North Pole",
            "sex": "M",
            "address": "North Pole",
            "mail": "north@pole.com",
            "username": "north",
            "job": "Explorer",
            "company": "Arctic Inc",
            "ssn": "111-11-1111",
            "residence": "Ice Street",
            "website": "www.north.com",
        },
        {
            "blood_group": "B+",
            "current_location": (-90, -180),  # South Pole
            "birthdate": datetime.datetime(1990, 1, 1),
            "name": "South Pole",
            "sex": "F",
            "address": "South Pole",
            "mail": "south@pole.com",
            "username": "south",
            "job": "Explorer",
            "company": "Antarctic Inc",
            "ssn": "222-22-2222",
            "residence": "Snow Street",
            "website": "www.south.com",
        },
    ]
    result = get_mean_current_location_dict(profiles)
    assert result == (0, 0), "Average of extreme coordinates should be (0, 0)"


def test_same_birthdate():
    """
    Test age calculations with identical birthdates.

    Verifies that:
        - Both oldest age and average age functions work with identical dates
        - Results match expected age for the shared birthdate
    """
    same_date = datetime.datetime(1990, 1, 1)
    profiles = [
        {
            "blood_group": "A+",
            "current_location": (0, 0),
            "birthdate": same_date,
            "name": "Person 1",
            "sex": "M",
            "address": "Address 1",
            "mail": "person1@example.com",
            "username": "person1",
            "job": "Job 1",
            "company": "Company 1",
            "ssn": "111-11-1111",
            "residence": "Residence 1",
            "website": "www.person1.com",
        },
        {
            "blood_group": "B+",
            "current_location": (0, 0),
            "birthdate": same_date,
            "name": "Person 2",
            "sex": "F",
            "address": "Address 2",
            "mail": "person2@example.com",
            "username": "person2",
            "job": "Job 2",
            "company": "Company 2",
            "ssn": "222-22-2222",
            "residence": "Residence 2",
            "website": "www.person2.com",
        },
    ]
    expected_age = datetime.datetime.now().year - same_date.year
    assert get_oldest_person_age_dict(profiles) == expected_age
    assert get_average_age_dict(profiles) == expected_age


def test_future_birthdate():
    """
    Test age calculations with future birthdates.

    Verifies that:
        - Functions raise ValueError for birthdates in the future
        - Error handling is consistent for both age calculation functions
    """
    future_date = datetime.datetime.now() + datetime.timedelta(days=365)
    profiles = [
        {
            "blood_group": "A+",
            "current_location": (0, 0),
            "birthdate": future_date,
            "name": "Future Person",
            "sex": "M",
            "address": "Future Address",
            "mail": "future@example.com",
            "username": "future",
            "job": "Future Job",
            "company": "Future Co",
            "ssn": "999-99-9999",
            "residence": "Future Residence",
            "website": "www.future.com",
        }
    ]
    with pytest.raises(ValueError):
        get_oldest_person_age_dict(profiles)
    with pytest.raises(ValueError):
        get_average_age_dict(profiles)
