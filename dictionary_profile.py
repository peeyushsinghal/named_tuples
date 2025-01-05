"""
Module for analyzing profile data stored in dictionary format.
Provides functions for statistical analysis of blood types, locations, and ages
from a collection of profile dictionaries.
"""

from faker import Faker
from decimal import Decimal
import numpy as np
import datetime
from typing import Any, List, Dict


def get_largest_blood_type_dict(profiles: List[Dict[str, Any]]) -> str:
    """
    Find the most common blood type among all profiles.

    Args:
        profiles (List[Dict[str, Any]]): List of profile dictionaries containing personal information,
            where each dictionary must have a 'blood_group' key

    Returns:
        str: The most frequent blood type in the dataset as a single-element set

    Raises:
        ValueError: If profiles list is empty
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    blood_group_dict = {}
    for profile in profiles:
        blood_group_dict[profile["blood_group"]] = (
            blood_group_dict.get(profile["blood_group"], 0) + 1
        )
    return {max(blood_group_dict, key=blood_group_dict.get)}


def get_mean_current_location_dict(
    profiles: List[Dict[str, Any]]
) -> tuple[float, float]:
    """
    Calculate the average geographical location across all profiles.

    Args:
        profiles (List[Dict[str, Any]]): List of profile dictionaries containing personal information,
            where each dictionary must have a 'current_location' key with (latitude, longitude) tuple

    Returns:
        tuple[float, float]: A tuple containing the mean latitude and longitude coordinates,
            returned as Decimal values for precision

    Raises:
        ValueError: If profiles list is empty
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    current_location_list = []
    for profile in profiles:
        current_location_list.append(profile["current_location"])

    current_location_array = np.array(current_location_list)
    mean_current_location = np.mean(current_location_array, axis=0)
    return tuple(Decimal(str(x)) for x in mean_current_location)


def get_oldest_person_age_dict(profiles: List[Dict[str, Any]]) -> int:
    """
    Find the age of the oldest person in the profiles.

    Args:
        profiles (List[Dict[str, Any]]): List of profile dictionaries containing personal information,
            where each dictionary must have a 'birthdate' key with datetime value

    Returns:
        int: Age of the oldest person in years

    Raises:
        ValueError: If profiles list is empty or if oldest person's birthdate is None or in the future
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    oldest_person_birthdate = min(profiles, key=lambda x: x["birthdate"])["birthdate"]
    if (
        oldest_person_birthdate is None
        or oldest_person_birthdate.year > datetime.datetime.now().year
    ):
        raise ValueError("Oldest person birthdate is None or in the future")
    return datetime.datetime.now().year - oldest_person_birthdate.year


def get_average_age_dict(profiles: List[Dict[str, Any]]) -> float:
    """
    Calculate the average age across all profiles.

    Args:
        profiles (List[Dict[str, Any]]): List of profile dictionaries containing personal information,
            where each dictionary must have a 'birthdate' key with datetime value

    Returns:
        float: Mean age of all people in the profiles

    Raises:
        ValueError: If profiles list is empty or if sum of ages is less than or equal to 0
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    ages = [datetime.datetime.now().year - x["birthdate"].year for x in profiles]
    if len(ages) == 0 or sum(ages) <= 0:
        raise ValueError("Ages list is empty or sum of ages is less than or equal to 0")
    return sum(ages) / len(ages)


if __name__ == "__main__":
    fake = Faker()
    profiles = []
    for _ in range(10_000):
        profiles.append(fake.profile())

    print(get_largest_blood_type_dict(profiles))
    print(get_mean_current_location_dict(profiles))
    print(get_oldest_person_age_dict(profiles))
    print(get_average_age_dict(profiles))
