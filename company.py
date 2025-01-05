"""
Module for generating and analyzing stock market company data.
Provides functions to create random company profiles with stock information
and calculate market values using weighted averages.
"""

from faker import Faker
from collections import namedtuple
import random


def generate_companies(num_companies: int, random_seed: int = 42) -> list:
    """
    Generate a list of random company profiles with stock information.

    Args:
        num_companies (int): Number of companies to generate
        random_seed (int): Seed for random number generator
    Returns:
        list[Stock]: List of Stock named tuples containing company information:
            - name: Company name
            - symbol: Generated stock ticker symbol
            - open: Opening price (100-1000 range)
            - high: Highest price (within circuit breaker limits)
            - low: Lowest price (within circuit breaker limits)
            - close: Closing price (between low and high)
            - weight: Normalized weight (0-1, sum of all weights = 1)
    """
    Faker.seed(random_seed)
    fake = Faker()
    stock_keys = ["name", "symbol", "open", "high", "low", "close", "weight"]
    Stock = namedtuple("Stock", stock_keys)
    companies = []
    total_weight = 0
    circuit_breakers = random.uniform(0.1, 0.25)
    for _ in range(num_companies):
        company_name = fake.company()
        if "," in company_name:
            company_ticker = f'{company_name[0].upper()}{company_name.split(",")[1][1].upper()}{fake.random_letter().upper()}'
        elif "-" in company_name:
            company_ticker = f'{company_name[0].upper()}{company_name.split("-")[1][0].upper()}{fake.random_letter().upper()}'
        else:
            company_ticker = f"{company_name[:3].upper()}"

        if "and" in company_name or "AND" in company_name:
            company_ticker = (
                company_ticker[:2] + f'{company_name.split("and")[1][1].upper()}'
            )

        open_price = round(random.uniform(100, 1000), 2)
        high_price = round(
            random.uniform(open_price, open_price + circuit_breakers * open_price), 2
        )
        low_price = round(
            random.uniform(open_price - circuit_breakers * open_price, open_price), 2
        )
        close_price = round(random.uniform(low_price, high_price), 2)
        weight = round(random.uniform(0.1, 1.0), 2)
        total_weight += weight
        companies.append(
            Stock(
                name=company_name,
                symbol=company_ticker,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                weight=weight,
            )
        )

    updated_companies = []
    for company in companies:
        new_weight = company.weight / total_weight
        updated_companies.append(
            Stock(
                name=company.name,
                symbol=company.symbol,
                open=company.open,
                high=company.high,
                low=company.low,
                close=company.close,
                weight=round(new_weight, 3),
            )
        )
    del companies
    return updated_companies


def calculate_stock_market_value(companies: list) -> tuple[float, float, float, float]:
    """
    Calculate weighted market values for different price points.

    Args:
        companies (list[Stock]): List of Stock named tuples containing company information

    Returns:
        tuple[float, float, float, float]: Tuple containing:
            - Weighted average of opening prices
            - Weighted average of high prices
            - Weighted average of low prices
            - Weighted average of closing prices
    """
    open_value = round(sum(company.open * company.weight for company in companies), 2)
    high_value = round(sum(company.high * company.weight for company in companies), 2)
    low_value = round(sum(company.low * company.weight for company in companies), 2)
    close_value = round(sum(company.close * company.weight for company in companies), 2)
    return open_value, high_value, low_value, close_value


if __name__ == "__main__":
    companies = generate_companies(5, random_seed=42)
    open_value, high_value, low_value, close_value = calculate_stock_market_value(
        companies
    )
    print(f"Open Value: {open_value}")
    print(f"High Value: {high_value}")
    print(f"Low Value: {low_value}")
    print(f"Close Value: {close_value}")
