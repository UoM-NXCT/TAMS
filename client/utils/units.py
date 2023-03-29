"""This software has to handle a lot of different units. When stored in the library and
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
    """Convert a value to the base unit for the given unit.

    :param given_value: value to convert
    :param given_unit: unit of the value
    :return: value in base units and the base unit, as a tuple
    """
    if len(given_unit) > 1:
        # Each prefix is one character long
        # Note: this is not true for the SI prefix deca (da), but we don't use that
        given_prefix: str = given_unit[0]
        given_prefix_exponent: int = prefix_exponents[given_prefix]

        # The SI unit is the rest of the string
        si_unit: str = given_unit[1:]
    elif len(given_unit) == 1:
        # Given unit is an SI unit
        given_prefix_exponent = 0
        si_unit = given_unit
    else:
        raise ValueError("No unit given")

    # Get the target prefix for the SI unit
    target_prefix: str = base_units[si_unit]
    target_prefix_exponent: int = prefix_exponents[target_prefix]

    # Calculate the exponent difference
    exponent_difference: int = given_prefix_exponent - target_prefix_exponent
    conversion_factor: int | float = 10**exponent_difference

    # Convert the new value
    new_value: int | float = given_value * conversion_factor
    new_unit: str = f"{target_prefix}{si_unit}"

    return new_value, new_unit
