# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

import random
import re
import string

import pytest
from pydantic import ValidationError

from openadr3_client.extensions.resource_group.models.resource_group import (
    ExistingResourceGroup,
    NewResourceGroup,
    ResourceGroupChild,
    ResourceGroupUpdate,
)


def test_new_resource_group_creation_guard() -> None:
    """NewResourceGroup can only be used to create once."""
    group = NewResourceGroup(resource_group_name="RG-1")

    with group.with_creation_guard():
        pass

    with (
        pytest.raises(ValueError, match=re.escape("CreationGuarded object has already been created.")),
        group.with_creation_guard(),
    ):
        pass


def test_resource_group_name_too_long() -> None:
    """resource_group_name is capped at 128 characters."""
    long_name = "".join(random.choices(string.ascii_letters, k=129))
    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewResourceGroup(resource_group_name=long_name)


def test_new_resource_group_serializes_with_camel_aliases() -> None:
    """Serialized request uses camelCase aliases and RESOURCE_GROUP object type."""
    group = NewResourceGroup(
        resource_group_name="RG-1",
        targets=("group-1",),
        children=(ResourceGroupChild(type="ven_resource", id="res-123"),),
    )
    dumped = group.model_dump(by_alias=True, mode="json")
    assert dumped["resourceGroupName"] == "RG-1"
    assert dumped["objectType"] == "RESOURCE_GROUP"
    assert dumped["targets"] == ["group-1"]
    assert dumped["children"] == [{"type": "ven_resource", "id": "res-123"}]


def test_child_type_rejects_invalid_value() -> None:
    """ResourceGroupChild.type only accepts the two enum members."""
    with pytest.raises(ValidationError):
        _ = ResourceGroupChild(type="not_a_type", id="x")  # type: ignore[arg-type]


def test_existing_resource_group_parses_obfuscated_empty_children() -> None:
    """A server response with no children parses to an empty tuple (VEN obfuscation)."""
    parsed = ExistingResourceGroup.model_validate(
        {
            "id": "rg-1",
            "createdDateTime": "2024-01-01T00:00:00Z",
            "modificationDateTime": "2024-01-01T00:00:00Z",
            "objectType": "RESOURCE_GROUP",
            "resourceGroupName": "RG-1",
        }
    )
    assert parsed.children == ()
    assert parsed.name == "RG-1"


def test_existing_resource_group_update_returns_updated_copy() -> None:
    """Calling .update() on an ExistingResourceGroup returns a new, separate instance with the updated fields applied."""
    existing = ExistingResourceGroup.model_validate(
        {
            "id": "rg-1",
            "createdDateTime": "2024-01-01T00:00:00Z",
            "modificationDateTime": "2024-01-01T00:00:00Z",
            "objectType": "RESOURCE_GROUP",
            "resourceGroupName": "RG-1",
        }
    )
    updated = existing.update(ResourceGroupUpdate(resource_group_name="RG-1b"))
    assert isinstance(updated, ExistingResourceGroup)
    assert updated.resource_group_name == "RG-1b"
    assert updated.id == "rg-1"
