# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for ValuesMap Pydantic schema integration."""

import pytest
from pydantic import TypeAdapter

from openadr3_client._models.common.attribute import Attribute
from openadr3_client._models.common.value_map_collection import ValuesMap
from openadr3_client._models.common.ven_resource_attribute_type import VenResourceAttributeType

_adapter = TypeAdapter(ValuesMap[VenResourceAttributeType, Attribute])


def test_values_map_deserialize_known_type() -> None:
    """Known enum value deserializes correctly."""
    result = _adapter.validate_python([{"type": "LOCATION", "values": [40.57, -73.96]}])

    assert isinstance(result, ValuesMap)
    assert len(result) == 1
    assert result[0].type == VenResourceAttributeType.LOCATION
    assert result[0].values == (40.57, -73.96)


def test_values_map_deserialize_unknown_type_added_to_enum() -> None:
    """Unknown type string is added to enum via _missing_ and deserializes correctly."""
    result = _adapter.validate_python([{"type": "MY_CUSTOM_ATTR", "values": ["custom-value"]}])

    assert isinstance(result, ValuesMap)
    assert len(result) == 1
    assert result[0].type == VenResourceAttributeType("MY_CUSTOM_ATTR")
    assert result[0].values == ("custom-value",)


def test_values_map_get_by_type_known() -> None:
    """get_by_type returns correct entry for known type."""
    result = _adapter.validate_python([{"type": "DESCRIPTION", "values": ["a ven"]}])

    entry = result.get_by_type(VenResourceAttributeType.DESCRIPTION)
    assert entry is not None
    assert entry.values == ("a ven",)


def test_values_map_get_by_type_missing_returns_none() -> None:
    """get_by_type returns None when key not present."""
    result = _adapter.validate_python([{"type": "DESCRIPTION", "values": ["a ven"]}])

    assert result.get_by_type(VenResourceAttributeType.LOCATION) is None


def test_values_map_round_trip() -> None:
    """Serialization round-trips back to a plain list."""
    raw = [{"type": "MAX_POWER_CONSUMPTION", "values": [7.5]}]
    result = _adapter.validate_python(raw)
    serialized = _adapter.dump_python(result)

    assert isinstance(serialized, list)
    assert serialized[0]["type"] == "MAX_POWER_CONSUMPTION"
    assert serialized[0]["values"] == (7.5,)


def test_values_map_get_by_type_unknown_warns_on_duplicate() -> None:
    """Warns when multiple entries share the same type key."""
    result: ValuesMap[VenResourceAttributeType, Attribute] = ValuesMap(
        [
            Attribute(type=VenResourceAttributeType.DESCRIPTION, values=("first",)),
            Attribute(type=VenResourceAttributeType.DESCRIPTION, values=("second",)),
        ]
    )

    with pytest.warns(UserWarning, match="Multiple valueMap entries found"):
        entry = result.get_by_type(VenResourceAttributeType.DESCRIPTION)

    assert entry is not None
    assert entry.values == ("first",)
