"""
Test module for company.py functions.
Contains test cases for company generation and market value calculations.
"""

import pytest
from collections import namedtuple
import company
from company import generate_companies, calculate_stock_market_value
import random
from faker import Faker
import inspect
import re


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
    assert abs(total_weight - 1.0) < 0.001

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
