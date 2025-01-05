"""
Module for analyzing profile data stored in namedtuple format.
Provides functions for statistical analysis of blood types, locations, and ages
from a collection of profile namedtuples.
"""

from faker import Faker
from collections import namedtuple
from decimal import Decimal
import numpy as np
import datetime
from typing import Any, List


def get_largest_blood_type(profiles: List["Profile"]) -> str:
    """
    Find the most common blood type among all profiles.

    Args:
        profiles (list[Profile]): List of Profile named tuples containing personal information

    Returns:
        str: The most frequent blood type in the dataset as a single-element set
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    blood_group_dict = {}
    for profile in profiles:
        blood_group_dict[profile.blood_group] = (
            blood_group_dict.get(profile.blood_group, 0) + 1
        )
    return {max(blood_group_dict, key=blood_group_dict.get)}


def get_mean_current_location(profiles: List["Profile"]) -> tuple[float, float]:
    """
    Calculate the average geographical location across all profiles.

    Args:
        profiles (list[Profile]): List of Profile named tuples containing personal information

    Returns:
        tuple[float, float]: A tuple containing the mean latitude and longitude coordinates
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    current_location_list = []
    for profile in profiles:
        current_location_list.append(profile.current_location)

    current_location_array = np.array(current_location_list)
    mean_current_location = np.mean(current_location_array, axis=0)
    return tuple(Decimal(str(x)) for x in mean_current_location)


def get_oldest_person_age(profiles: List["Profile"]) -> int:
    """
    Find the age of the oldest person in the profiles.

    Args:
        profiles (list[Profile]): List of Profile named tuples containing personal information

    Returns:
        int: Age of the oldest person in years
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    oldest_person_birthdate = min(profiles, key=lambda x: x.birthdate).birthdate
    if (
        oldest_person_birthdate is None
        or oldest_person_birthdate.year > datetime.datetime.now().year
    ):
        raise ValueError("Oldest person birthdate is None or in the future")
    return datetime.datetime.now().year - oldest_person_birthdate.year


def get_average_age(profiles: List["Profile"]) -> float:
    """
    Calculate the average age across all profiles.

    Args:
        profiles (list[Profile]): List of Profile named tuples containing personal information

    Returns:
        float: Mean age of all people in the profiles
    """
    if not profiles or len(profiles) == 0:
        raise ValueError("Profiles list is empty")

    ages = [datetime.datetime.now().year - x.birthdate.year for x in profiles]
    if len(ages) == 0 or sum(ages) <= 0:
        raise ValueError("Ages list is empty or sum of ages is less than or equal to 0")
    return sum(ages) / len(ages)


if __name__ == "__main__":
    fake = Faker()
    Profile = namedtuple("Profile", fake.profile().keys())
    profile_x = Profile(**fake.profile())
    print(profile_x.current_location)
    profiles = []
    for _ in range(10_000):
        profiles.append(Profile(**fake.profile()))

    print(get_largest_blood_type(profiles))
    print(get_mean_current_location(profiles))
    print(get_oldest_person_age(profiles))
    print(get_average_age(profiles))
