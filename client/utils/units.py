"""
This software has to handle a lot of different units. When stored in the library and 
database, we will use a set of standard units for each measurement.

Measurement type | SI unit | Base unit
-----------------+---------+----------
Voltage          | V       | kV
Current          | A       | uA
Metres           | m       | mm
"""

base_units: dict[str, str] = {
    "V": "k",
    "A": "u",
    "m": "m",
}

prefix_exponents: dict[str, int] = {
    "k": 3,
    "u": -6,
    "m": -3,
}


def to_base_unit(value: int | float, unit: str):
    """Convert a value to the base unit for the given unit."""

    # Each prefix is one character long
    # Note: this is not true for the SI prefix "deca" (da), but we don't use that

    prefix: str = unit[0]
    given_prefix_exponent: int = prefix_exponents[prefix]

    # The SI unit is the rest of the string
    si_unit: str = unit[1:]

    # Get the target prefix for the SI unit
    target_prefix: str = base_units[si_unit]
    target_prefix_exponent: int = prefix_exponents[target_prefix]

    # Calculate the exponent difference
    exponent_difference: int = given_prefix_exponent - target_prefix_exponent
    conversion_factor: float = 10**exponent_difference
    return value * conversion_factor
