from dictionary_profile import (
    get_largest_blood_type_dict,
    get_mean_current_location_dict,
    get_oldest_person_age_dict,
    get_average_age_dict,
)
from named_tuple_profile import (
    get_largest_blood_type,
    get_mean_current_location,
    get_oldest_person_age,
    get_average_age,
)
from time import perf_counter
from faker import Faker
from collections import namedtuple
from unittest.mock import patch


def time_it(func):
    """
    Decorator to time the execution of a function.
    """

    def inner(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f"{func.__name__} took {end - start} seconds")
        return result

    return inner


@time_it
def test_named_tuple(num_profiles):
    fake = Faker()
    Profile = namedtuple("Profile", fake.profile().keys())
    profiles = []
    for _ in range(num_profiles):
        profiles.append(Profile(**fake.profile()))

    get_largest_blood_type(profiles)
    get_mean_current_location(profiles)
    get_oldest_person_age(profiles)
    get_average_age(profiles)


@time_it
def test_dict(num_profiles):
    fake = Faker()
    profiles = []
    for _ in range(num_profiles):
        profiles.append(fake.profile())
    get_largest_blood_type_dict(profiles)
    get_mean_current_location_dict(profiles)
    get_oldest_person_age_dict(profiles)
    get_average_age_dict(profiles)


def main():
    num_profiles = 20_000

    # Capture dictionary test output
    with patch("builtins.print") as mock_print_dict:
        test_dict(num_profiles)
        dict_time = mock_print_dict.call_args[0][0]  # Get the printed string

    # Capture named tuple test output
    with patch("builtins.print") as mock_print_tuple:
        test_named_tuple(num_profiles)
        tuple_time = mock_print_tuple.call_args[0][0]  # Get the printed string

    # Extract just the numbers for comparison
    dict_seconds = float(dict_time.split()[2])
    tuple_seconds = float(tuple_time.split()[2])

    # Compare and print results
    difference = abs(dict_seconds - tuple_seconds)
    faster = "Dictionary" if dict_seconds < tuple_seconds else "Named tuple"
    print(f"\nComparison:")
    print(f"Dictionary time: {dict_seconds:.2f} seconds")
    print(f"Named tuple time: {tuple_seconds:.2f} seconds")
    print(f"Difference: {difference:.2f} seconds")
    print(f"{faster} implementation was faster")


if __name__ == "__main__":
    main()
