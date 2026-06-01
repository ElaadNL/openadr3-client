# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the domain models related to program attributes."""

from enum import StrEnum
from typing import Any


class ProgramAttributeType(StrEnum):
    """Enumeration of the standard program attribute types of OpenADR 3.1."""

    PROGRAM_LONG_NAME = "PROGRAM_LONG_NAME"
    """Long name of program for human readability."""

    RETAILER_NAME = "RETAILER_NAME"
    """Short name of energy retailer providing the program."""

    RETAILER_LONG_NAME = "RETAILER_LONG_NAME"
    """Long name of energy retailer for human readability."""

    PROGRAM_TYPE = "PROGRAM_TYPE"
    """A program defined categorization."""

    COUNTRY = "COUNTRY"
    """Alpha-2 code per ISO 3166-1."""

    PRINCIPAL_SUBDIVISION = "PRINCIPAL_SUBDIVISION"
    """Coding per ISO 3166-2. E.g. state in US."""

    BINDING_EVENTS = "BINDING_EVENTS"
    """True if events are fixed once transmitted."""

    LOCAL = "LOCAL"
    """Indicates that data in the program have been created by a local VTN."""

    @classmethod
    def _missing_(cls: type["ProgramAttributeType"], value: Any) -> "ProgramAttributeType":  # noqa: ANN401
        """
        Add support for custom program attribute types.

        Args:
            cls: The program attribute type class.
            value: The custom enum value to add.

        Returns:
            The new program attribute type.

        """
        min_length = 1
        max_length = 128
        if isinstance(value, str) and min_length <= len(value) <= max_length:
            new_member = str.__new__(cls, value)
            new_member._name_ = value
            new_member._value_ = value
            cls._member_map_[value] = new_member
            return new_member
        exc_msg = f"Invalid program attribute type value: {value}"
        raise ValueError(exc_msg)
