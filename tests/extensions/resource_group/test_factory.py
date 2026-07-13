# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from openadr3_client.extensions.resource_group import (
    NewResourceGroup,
    ReadOnlyResourceGroupsInterface,
    ReadWriteResourceGroupsInterface,
    ResourceGroupClientFactory,
)


def test_create_bl_client_returns_read_write_interface() -> None:
    """Test that BL client creation returns a ReadWrite interface."""
    client = ResourceGroupClientFactory.create_bl_client(
        vtn_base_url="https://vtn.example",
        client_id="bl",
        client_secret="secret",
        token_url="https://vtn.example/auth/token",
        scopes=["read_all", "write_programs"],
    )
    assert isinstance(client, ReadWriteResourceGroupsInterface)
    assert hasattr(client, "create_resource_group")


def test_create_ven_client_returns_read_only_interface() -> None:
    """Test that VEN client creation returns a ReadOnly interface without write methods."""
    client = ResourceGroupClientFactory.create_ven_client(
        vtn_base_url="https://vtn.example",
        client_id="ven",
        client_secret="secret",
        token_url="https://vtn.example/auth/token",
        scopes=["read_ven_objects"],
    )
    assert isinstance(client, ReadOnlyResourceGroupsInterface)
    assert not isinstance(client, ReadWriteResourceGroupsInterface)
    assert not hasattr(client, "create_resource_group")


def test_public_exports_are_importable() -> None:
    """Test that public module exports are properly importable."""
    assert NewResourceGroup.__name__ == "NewResourceGroup"
