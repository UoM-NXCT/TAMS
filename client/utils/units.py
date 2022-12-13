"""
This software has to handle a lot of different units. When stored in the library and 
database, we will use a set of standard units for each measurement.

The base units are selected for what makes the most sense for CT data.

Measurement type | SI unit | Base unit
-----------------+---------+----------
Voltage          | V       | kV
Current          | A       | uA
Metres           | m       | mm
"""

base_units: dict[str, str] = {
    "V": "k",  # kV
    "A": "u",  # uA
    "m": "m",  # mm
}

prefix_exponents: dict[str, int] = {
    "P": 15,
    "T": 12,
    "G": 9,
    "M": 6,
    "k": 3,
    "m": -3,
    "u": -6,
    "n": -9,
    "p": -12,
    "f": -15,
}


def to_base_unit(given_value: int | float, given_unit: str) -> tuple[int | float, str]:
    """Convert a value to the base unit for the given unit."""

    # Each prefix is one character long
    # Note: this is not true for the SI prefix deca (da), but we don't use that
    given_prefix: str = given_unit[0]
    given_prefix_exponent: int = prefix_exponents[given_prefix]

    # The SI unit is the rest of the string
    si_unit: str = given_unit[1:]

    # Get the target prefix for the SI unit
    target_prefix: str = base_units[si_unit]
    target_prefix_exponent: int = prefix_exponents[target_prefix]

    # Calculate the exponent difference
    exponent_difference: int = given_prefix_exponent - target_prefix_exponent
    conversion_factor: float = 10**exponent_difference
    return given_value * conversion_factor, f"{target_prefix}{si_unit}"
