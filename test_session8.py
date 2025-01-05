import pytest
from collections import namedtuple
import company
from company import generate_companies, calculate_stock_market_value
import random
from faker import Faker
import inspect
import re
from decimal import Decimal
import datetime
from named_tuple_profile import (
    get_largest_blood_type,
    get_mean_current_location,
    get_oldest_person_age,
    get_average_age,
)
from dictionary_profile import (
    get_largest_blood_type_dict,
    get_mean_current_location_dict,
    get_oldest_person_age_dict,
    get_average_age_dict,
)


"""
Test module for company.py functions.
Contains test cases for company generation and market value calculations.
"""
@pytest.fixture
def sample_companies():
    """
    Fixture providing sample company data for testing.

    Returns:
        list[Stock]: A list of Stock named tuples with test data
    """
    Stock = namedtuple(
        "Stock", ["name", "symbol", "open", "high", "low", "close", "weight"]
    )
    return [
        Stock(
            name="Tech Corp",
            symbol="TCX",
            open=500.00,
            high=550.00,
            low=480.00,
            close=525.00,
            weight=0.5,
        ),
        Stock(
            name="Finance Inc",
            symbol="FIN",
            open=200.00,
            high=220.00,
            low=190.00,
            close=210.00,
            weight=0.3,
        ),
        Stock(
            name="Energy Ltd",
            symbol="ENG",
            open=300.00,
            high=320.00,
            low=290.00,
            close=310.00,
            weight=0.2,
        ),
    ]


def test_generate_companies():
    """
    Test company generation function.

    Verifies that:
        - Correct number of companies are generated
        - Stock symbols are valid
        - Prices are within expected ranges
        - Weights sum to 1
    """
    num_companies = 5
    companies = generate_companies(num_companies)

    assert len(companies) == num_companies

    # Test weight normalization
    total_weight = sum(company.weight for company in companies)
    assert abs(total_weight - 1.0) < 0.01

    for company in companies:
        # Test price ranges
        assert 100 <= company.open <= 1000
        assert company.low <= company.open <= company.high
        assert company.low <= company.close <= company.high

        # Test stock symbol format
        assert len(company.symbol) <= 4
        assert company.symbol.isupper()


def test_calculate_stock_market_value(sample_companies):
    """
    Test market value calculations with sample data.

    Verifies that:
        - Weighted averages are calculated correctly
        - Results are rounded to 2 decimal places
    """
    open_val, high_val, low_val, close_val = calculate_stock_market_value(
        sample_companies
    )

    # Expected values based on sample data
    expected_open = 500.00 * 0.5 + 200.00 * 0.3 + 300.00 * 0.2
    expected_high = 550.00 * 0.5 + 220.00 * 0.3 + 320.00 * 0.2
    expected_low = 480.00 * 0.5 + 190.00 * 0.3 + 290.00 * 0.2
    expected_close = 525.00 * 0.5 + 210.00 * 0.3 + 310.00 * 0.2

    assert open_val == round(expected_open, 2)
    assert high_val == round(expected_high, 2)
    assert low_val == round(expected_low, 2)
    assert close_val == round(expected_close, 2)


def test_price_constraints():
    """
    Test that generated prices follow market constraints.

    Verifies that:
        - High price is always highest
        - Low price is always lowest
        - Open and close prices are between high and low
        - Circuit breaker limits are respected
    """
    companies = generate_companies(10)

    for company in companies:
        assert company.low <= company.open <= company.high
        assert company.low <= company.close <= company.high

        # Test circuit breaker limits (10-25% from open)
        max_allowed_move = company.open * 0.25
        assert company.high - company.open <= max_allowed_move
        assert company.open - company.low <= max_allowed_move


def test_stock_symbol_generation():
    """
    Test stock symbol generation rules.

    Verifies that:
        - Symbols are correctly generated for different company name formats
        - Symbols are uppercase and valid length
    """
    fake = Faker()
    fake.seed_instance(12345)  # For reproducible tests

    # Test company with comma
    Stock = namedtuple("Stock", ["name", "symbol"])
    company = Stock(name="Smith, Johnson and Co", symbol="SJX")
    assert len(company.symbol) == 3
    assert company.symbol.isupper()

    # Test company with hyphen
    company = Stock(name="Tech-Solutions Inc", symbol="TSX")
    assert len(company.symbol) == 3
    assert company.symbol.isupper()


def test_empty_input():
    """
    Test handling of empty company list.

    Verifies that:
        - Market value calculation handles empty input appropriately
    """
    empty_companies = []
    open_val, high_val, low_val, close_val = calculate_stock_market_value(
        empty_companies
    )
    assert open_val == 0
    assert high_val == 0
    assert low_val == 0
    assert close_val == 0


def test_single_company():
    """
    Test with single company.

    Verifies that:
        - Market values match company prices when only one company exists
        - Weight normalization works with single company
    """
    companies = generate_companies(1)
    assert len(companies) == 1
    assert companies[0].weight == 1.0

    open_val, high_val, low_val, close_val = calculate_stock_market_value(companies)
    assert open_val == companies[0].open
    assert high_val == companies[0].high
    assert low_val == companies[0].low
    assert close_val == companies[0].close


def test_weight_normalization():
    """
    Test weight normalization.

    Verifies that:
        - Weights always sum to 1
        - Weights are proportionally distributed
    """
    for num_companies in [2, 5, 10]:
        companies = generate_companies(num_companies)
        total_weight = sum(company.weight for company in companies)
        assert abs(total_weight - 1.0) < 0.005

        # Test that no company has zero weight
        for company in companies:
            assert company.weight > 0


def test_reproducibility():
    """
    Test reproducibility with fixed random seed.

    Verifies that:
        - Same seed produces same results
        - Different seeds produce different results
    """
    random.seed(42)
    companies1 = generate_companies(5)

    random.seed(42)
    companies2 = generate_companies(5)

    # Same seed should produce same results
    for c1, c2 in zip(companies1, companies2):
        assert c1.name == c2.name
        assert c1.symbol == c2.symbol
        assert c1.open == c2.open
        assert c1.weight == c2.weight


def test_price_rounding():
    """
    Test price rounding behavior.

    Verifies that:
        - All prices are rounded to 2 decimal places
        - Market values are rounded to 2 decimal places
    """
    companies = generate_companies(5)

    for company in companies:
        assert round(company.open, 2) == company.open
        assert round(company.high, 2) == company.high
        assert round(company.low, 2) == company.low
        assert round(company.close, 2) == company.close
        assert round(company.weight, 3) == company.weight

    open_val, high_val, low_val, close_val = calculate_stock_market_value(companies)
    assert round(open_val, 2) == open_val
    assert round(high_val, 2) == high_val
    assert round(low_val, 2) == low_val
    assert round(close_val, 2) == close_val

def test_indentations():
    """ Returns pass if used four spaces for each level of syntactically \
    significant indenting."""
    lines = inspect.getsource(company)
    spaces = re.findall("\n +.", lines)
    for space in spaces:
        assert len(space) % 4 == 2, "Your script contains misplaced indentations"
        assert (
            len(re.sub(r"[^ ]", "", space)) % 4 == 0
        ), "Your code indentation does not follow PEP8 guidelines"

"""
Test module for dictionary_profile.py functions.
Contains test cases for profile data analysis functions including blood type, location, and age calculations.
"""



@pytest.fixture
def sample_profiles_dict():
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


def test_get_largest_blood_type_dict(sample_profiles_dict):
    """
    Test get_largest_blood_type_dict function with sample profiles.

    Verifies that:
        - Function correctly identifies 'A+' as most common blood type
        - Returns result as a single-element set
    """
    result = get_largest_blood_type_dict(sample_profiles_dict)
    assert result == {"A+"}, "Should return {'A+'} as it appears twice"


def test_get_mean_current_location_dict(sample_profiles_dict):
    """
    Test get_mean_current_location_dict function with sample profiles.

    Verifies that:
        - Function correctly calculates average latitude and longitude
        - Result is within 0.01 decimal degrees of expected values
        - Returns coordinates as Decimal values for precision
    """
    result = get_mean_current_location_dict(sample_profiles_dict)
    assert (
        abs(result[0] - Decimal("42.0908")) < 0.01
    ), "Latitude should be approximately equal"
    assert (
        abs(result[1] - Decimal("-64.1258")) < 0.01
    ), "Longitude should be approximately equal"


def test_get_oldest_person_age_dict(sample_profiles_dict):
    """
    Test get_oldest_person_age_dict function with sample profiles.

    Verifies that:
        - Function correctly identifies oldest person (Jane, born 1985)
        - Returns correct age based on current year
    """
    current_year = datetime.datetime.now().year
    result = get_oldest_person_age_dict(sample_profiles_dict)
    expected = current_year - 1985  # Jane's birth year
    assert result == expected, f"Should return {expected} years"


def test_get_average_age_dict(sample_profiles_dict):
    """
    Test get_average_age_dict function with sample profiles.

    Verifies that:
        - Function correctly calculates mean age of all profiles
        - Result is within 0.01 years of expected value
    """
    current_year = datetime.datetime.now().year
    result = get_average_age_dict(sample_profiles_dict)
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


def test_single_profile(sample_profiles_dict):
    """
    Test all functions with single profile.

    Verifies that:
        - Functions work correctly with single-element list
        - Results match expected values for John's profile
    """
    single_profile = [sample_profiles_dict[0]]
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


def test_duplicate_profiles(sample_profiles_dict):
    """
    Test functions with duplicated profile data.

    Verifies that:
        - Functions handle duplicate data correctly
        - Most common blood type remains 'A+' when profiles are duplicated
    """
    duplicates = sample_profiles_dict + sample_profiles_dict                
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



"""
Test module for named_tuple_profile.py functions.
Contains test cases for profile data analysis functions including blood type, location, and age calculations.
"""

# Create a test Profile namedtuple
Profile = namedtuple(
    "Profile",
    [
        "blood_group",
        "current_location",
        "birthdate",
        "name",
        "sex",
        "address",
        "mail",
        "username",
        "job",
        "company",
        "ssn",
        "residence",
        "website",
    ],
)


@pytest.fixture
def sample_profiles():
    """
    Fixture providing sample profile data for testing.

    Returns:
        list[Profile]: A list of three Profile named tuples with test data:
            - John Doe from NYC (A+ blood type, born 1990)
            - Jane Smith from LA (B- blood type, born 1985)
            - Bob Wilson from London (A+ blood type, born 1995)
    """
    return [
        Profile(
            blood_group="A+",
            current_location=(
                Decimal("40.7128"),
                Decimal("-74.0060"),
            ),  # NYC coordinates
            birthdate=datetime.datetime(1990, 1, 1),
            name="John Doe",
            sex="M",
            address="123 Main St",
            mail="john@example.com",
            username="johnd",
            job="Engineer",
            company="Tech Corp",
            ssn="123-45-6789",
            residence="456 Home St",
            website="www.john.com",
        ),
        Profile(
            blood_group="B-",
            current_location=(
                Decimal("34.0522"),
                Decimal("-118.2437"),
            ),  # LA coordinates
            birthdate=datetime.datetime(1985, 6, 15),
            name="Jane Smith",
            sex="F",
            address="789 Oak St",
            mail="jane@example.com",
            username="janes",
            job="Designer",
            company="Design Co",
            ssn="987-65-4321",
            residence="321 House St",
            website="www.jane.com",
        ),
        Profile(
            blood_group="A+",
            current_location=(
                Decimal("51.5074"),
                Decimal("-0.1278"),
            ),  # London coordinates
            birthdate=datetime.datetime(1995, 12, 31),
            name="Bob Wilson",
            sex="M",
            address="10 Park Lane",
            mail="bob@example.com",
            username="bobw",
            job="Manager",
            company="Manage Ltd",
            ssn="456-78-9012",
            residence="15 Home Ave",
            website="www.bob.com",
        ),
    ]


def test_get_largest_blood_type(sample_profiles):
    """
    Test get_largest_blood_type function with sample profiles.

    Verifies that:
        - Function correctly identifies 'A+' as most common blood type
        - Returns result as a single-element set
    """
    result = get_largest_blood_type(sample_profiles)
    assert result == {"A+"}, "Should return {'A+'} as it appears twice"


def test_get_mean_current_location(sample_profiles):
    """
    Test get_mean_current_location function with sample profiles.

    Verifies that:
        - Function correctly calculates average latitude and longitude
        - Result is within 0.01 decimal degrees of expected values
        - Returns coordinates as Decimal values for precision
    """
    result = get_mean_current_location(sample_profiles)
    assert (
        abs(result[0] - Decimal("42.0908")) < 0.01
    ), "Latitude should be approximately equal"
    assert (
        abs(result[1] - Decimal("-64.1258")) < 0.01
    ), "Longitude should be approximately equal"


def test_get_oldest_person_age(sample_profiles):
    """
    Test get_oldest_person_age function with sample profiles.

    Verifies that:
        - Function correctly identifies oldest person (Jane, born 1985)
        - Returns correct age based on current year
    """
    current_year = datetime.datetime.now().year
    result = get_oldest_person_age(sample_profiles)
    expected = current_year - 1985  # Jane's birth year
    assert result == expected, f"Should return {expected} years"


def test_get_average_age(sample_profiles):
    """
    Test get_average_age function with sample profiles.

    Verifies that:
        - Function correctly calculates mean age of all profiles
        - Result is within 0.01 years of expected value
    """
    current_year = datetime.datetime.now().year
    result = get_average_age(sample_profiles)
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
        get_largest_blood_type(empty_profiles)
    with pytest.raises(ValueError):
        get_mean_current_location(empty_profiles)
    with pytest.raises(ValueError):
        get_oldest_person_age(empty_profiles)
    with pytest.raises(ValueError):
        get_average_age(empty_profiles)


def test_single_profile(sample_profiles):
    """
    Test all functions with single profile.

    Verifies that:
        - Functions work correctly with single-element list
        - Results match expected values for John's profile
    """
    single_profile = [sample_profiles[0]]
    assert get_largest_blood_type(single_profile) == {"A+"}
    print(get_mean_current_location(single_profile))
    assert get_mean_current_location(single_profile) == (
        Decimal("40.7128"),
        Decimal("-74.0060"),
    )
    assert get_oldest_person_age(single_profile) == datetime.datetime.now().year - 1990
    assert get_average_age(single_profile) == datetime.datetime.now().year - 1990


def test_duplicate_profiles(sample_profiles):
    """
    Test functions with duplicated profile data.

    Verifies that:
        - Functions handle duplicate data correctly
        - Most common blood type remains 'A+' when profiles are duplicated
    """
    duplicates = sample_profiles + sample_profiles
    result = get_largest_blood_type(duplicates)
    assert result == {"A+"}, "Should still return {'A+'} with duplicated profiles"


def test_different_locations():
    """
    Test location calculation with extreme coordinates.

    Verifies that:
        - Function correctly averages extreme latitude/longitude values
        - North Pole (90, 180) and South Pole (-90, -180) average to (0, 0)
    """
    profiles = [
        Profile(
            blood_group="A+",
            current_location=(90, 180),  # North Pole
            birthdate=datetime.datetime(1990, 1, 1),
            name="North Pole",
            sex="M",
            address="North Pole",
            mail="north@pole.com",
            username="north",
            job="Explorer",
            company="Arctic Inc",
            ssn="111-11-1111",
            residence="Ice Street",
            website="www.north.com",
        ),
        Profile(
            blood_group="B+",
            current_location=(-90, -180),  # South Pole
            birthdate=datetime.datetime(1990, 1, 1),
            name="South Pole",
            sex="F",
            address="South Pole",
            mail="south@pole.com",
            username="south",
            job="Explorer",
            company="Antarctic Inc",
            ssn="222-22-2222",
            residence="Snow Street",
            website="www.south.com",
        ),
    ]
    result = get_mean_current_location(profiles)
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
        Profile(
            blood_group="A+",
            current_location=(0, 0),
            birthdate=same_date,
            name="Person 1",
            sex="M",
            address="Address 1",
            mail="person1@example.com",
            username="person1",
            job="Job 1",
            company="Company 1",
            ssn="111-11-1111",
            residence="Residence 1",
            website="www.person1.com",
        ),
        Profile(
            blood_group="B+",
            current_location=(0, 0),
            birthdate=same_date,
            name="Person 2",
            sex="F",
            address="Address 2",
            mail="person2@example.com",
            username="person2",
            job="Job 2",
            company="Company 2",
            ssn="222-22-2222",
            residence="Residence 2",
            website="www.person2.com",
        ),
    ]
    expected_age = datetime.datetime.now().year - same_date.year
    assert get_oldest_person_age(profiles) == expected_age
    assert get_average_age(profiles) == expected_age


def test_future_birthdate():
    """
    Test age calculations with future birthdates.

    Verifies that:
        - Functions raise ValueError for birthdates in the future
        - Error handling is consistent for both age calculation functions
    """
    future_date = datetime.datetime.now() + datetime.timedelta(days=365)
    profiles = [
        Profile(
            blood_group="A+",
            current_location=(0, 0),
            birthdate=future_date,
            name="Future Person",
            sex="M",
            address="Future Address",
            mail="future@example.com",
            username="future",
            job="Future Job",
            company="Future Co",
            ssn="999-99-9999",
            residence="Future Residence",
            website="www.future.com",
        )
    ]
    with pytest.raises(ValueError):
        get_oldest_person_age(profiles)
    with pytest.raises(ValueError):
        get_average_age(profiles)
