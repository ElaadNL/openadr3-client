from enum import StrEnum
from typing import Any


class Unit(StrEnum):
    """Enumeration of the units allowed by OpenADR 3."""

    KWH = "KWH"
    Therms = "THERMS"
    GHG = "GHG"
    Volts = "VOLTS"
    Amps = "AMPS"
    Celcius = "CELCIUS"
    Fahrenheit = "FAHRENHEIT"
    Percent = "PERCENT"
    KW = "KW"
    KVAH = "KVAH"
    KVARH = "KVARH"
    KVA = "KVA"
    KVAR = "KVAR"

    @classmethod
    def _missing_(cls: type["Unit"], value: Any) -> "Unit":  # noqa: ANN401
        """
        Add support for custom enum cases.

        Args:
            cls (type[&quot;EventPayloadType&quot;]): The enum class.
            value (Any): The custom enum value to add.

        Returns:
            Unit: The new enum type.

        """
        # Create a new enum member dynamically
        new_member = str.__new__(cls, value)
        new_member._name_ = value
        new_member._value_ = value
        # Add it to the enum
        cls._member_map_[value] = new_member
        return new_member
