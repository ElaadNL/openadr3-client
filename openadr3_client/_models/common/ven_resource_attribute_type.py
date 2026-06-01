# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the domain models related to VEN and resource attribute types."""

from enum import StrEnum
from typing import Any


class VenResourceAttributeType(StrEnum):
    """Enumeration of the standard VEN and resource attribute types of OpenADR 3."""

    LOCATION = "LOCATION"
    """Describes a single geographic point. Values[] contains 2 floats (longitude, latitude)."""

    AREA = "AREA"
    """Describes a geographic area. Values[] contains application specific data (e.g. GeoJSON)."""

    MAX_POWER_CONSUMPTION = "MAX_POWER_CONSUMPTION"
    """Maximum consumption in kiloWatts."""

    MAX_POWER_EXPORT = "MAX_POWER_EXPORT"
    """Maximum power the device can export in kiloWatts."""

    DESCRIPTION = "DESCRIPTION"
    """Free-form text tersely describing a VEN or resource."""

    @classmethod
    def _missing_(cls: type["VenResourceAttributeType"], value: Any) -> "VenResourceAttributeType":  # noqa: ANN401
        """
        Add support for custom VEN and resource attribute types.

        Args:
            cls: The VEN resource attribute type class.
            value: The custom enum value to add.

        Returns:
            The new VEN resource attribute type.

        """
        min_length = 1
        max_length = 128
        if isinstance(value, str) and min_length <= len(value) <= max_length:
            new_member = str.__new__(cls, value)
            new_member._name_ = value
            new_member._value_ = value
            cls._member_map_[value] = new_member
            return new_member
        exc_msg = f"Invalid VEN resource attribute type value: {value}"
        raise ValueError(exc_msg)
