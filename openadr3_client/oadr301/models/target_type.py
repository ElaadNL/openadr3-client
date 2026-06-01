# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the domain models related to target types."""

from enum import StrEnum
from typing import Any


class TargetType(StrEnum):
    """Enumeration of the standard target types of OpenADR 3.0.1."""

    POWER_SERVICE_LOCATION = "POWER_SERVICE_LOCATION"
    """A utility named specific location in geography or the distribution system."""

    SERVICE_AREA = "SERVICE_AREA"
    """A utility named geographic region."""

    GROUP = "GROUP"
    """A group identifier."""

    RESOURCE_NAME = "RESOURCE_NAME"
    """A resource name."""

    VEN_NAME = "VEN_NAME"
    """A VEN name."""

    EVENT_NAME = "EVENT_NAME"
    """An event name."""

    PROGRAM_NAME = "PROGRAM_NAME"
    """A program name."""

    @classmethod
    def _missing_(cls: type["TargetType"], value: Any) -> "TargetType":  # noqa: ANN401
        """
        Add support for custom target types.

        Args:
            cls: The target type class.
            value: The custom enum value to add.

        Returns:
            The new target type.

        """
        min_length = 1
        max_length = 128
        if isinstance(value, str) and min_length <= len(value) <= max_length:
            new_member = str.__new__(cls, value)
            new_member._name_ = value
            new_member._value_ = value
            cls._member_map_[value] = new_member
            return new_member
        exc_msg = f"Invalid target type value: {value}"
        raise ValueError(exc_msg)
