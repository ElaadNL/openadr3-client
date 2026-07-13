# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Integration tests for the resource group HTTP client (against the OpenLEADR-rs VTN)."""

import pytest
from requests import HTTPError

from openadr3_client.extensions.resource_group._client.http import (
    ResourceGroupsHttpInterface,
    ResourceGroupsReadOnlyHttpInterface,
)
from openadr3_client.extensions.resource_group.models.resource_group import (
    NewResourceGroup,
    ResourceGroupUpdate,
)
from tests.conftest import IntegrationTestVTNClient

# The pinned OpenLEADR-rs VTN testcontainer image (default v0.2.0-rc2, see
# tests/conftest.py `--openleadr-310-version`) predates resource group support,
# which landed in openleadr-rs 0.2.3. Until the pinned image is bumped to an
# NLFlex-capable version, these integration tests cannot run against the
# testcontainer. See plan Task 3 Step 1 and the Task 3 execution report.


def _bl_interface(client: IntegrationTestVTNClient) -> ResourceGroupsHttpInterface:
    return ResourceGroupsHttpInterface(
        base_url=client.vtn_base_url,
        config=client.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )


def test_create_and_get_resource_group(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """A BL client can create a resource group and read it back by id."""
    interface = _bl_interface(vtn_openadr_310_bl_token)

    created = interface.create_resource_group(
        NewResourceGroup(resource_group_name="RG-create", targets=("group-1",))
    )
    assert created.resource_group_name == "RG-create"
    assert created.id

    fetched = interface.get_resource_group_by_id(created.id)
    assert fetched.id == created.id

    interface.delete_resource_group_by_id(created.id)


def test_list_filters_by_name(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Listing with resource_group_name returns the matching group."""
    interface = _bl_interface(vtn_openadr_310_bl_token)
    created = interface.create_resource_group(NewResourceGroup(resource_group_name="RG-list"))
    try:
        results = interface.get_resource_groups(resource_group_name="RG-list")
        assert any(g.id == created.id for g in results)
    finally:
        interface.delete_resource_group_by_id(created.id)


def test_update_resource_group(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """A BL client can update a resource group's name."""
    interface = _bl_interface(vtn_openadr_310_bl_token)
    created = interface.create_resource_group(NewResourceGroup(resource_group_name="RG-update"))
    try:
        updated = interface.update_resource_group_by_id(
            created.id, ResourceGroupUpdate(resource_group_name="RG-updated")
        )
        assert updated.resource_group_name == "RG-updated"
    finally:
        interface.delete_resource_group_by_id(created.id)


def test_get_resource_group_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Fetching a non-existent id raises an HTTP error."""
    interface = _bl_interface(vtn_openadr_310_bl_token)
    with pytest.raises(HTTPError):
        interface.get_resource_group_by_id("does-not-exist")


def test_ven_cannot_create_resource_group(vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """The read-only VEN interface exposes no create method (writes are BL-only, enforced structurally)."""
    ven_read_only = ResourceGroupsReadOnlyHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )
    # Read-only interface deliberately exposes no create method.
    assert not hasattr(ven_read_only, "create_resource_group")
