# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""
Mocked-session unit tests for the resource group HTTP client.

These tests stub `interface.session` to verify the client issues the expected
HTTP verb/URL/body for each operation without needing a live VTN.
"""

from unittest.mock import MagicMock

import pytest

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.extensions.resource_group._client.filters import PaginationFilter, TargetFilter
from openadr3_client.extensions.resource_group._client.http import (
    BASE_PREFIX,
    ResourceGroupsHttpInterface,
    ResourceGroupsReadOnlyHttpInterface,
)
from openadr3_client.extensions.resource_group.models.resource_group import (
    NewResourceGroup,
    ResourceGroupUpdate,
)

_BASE_URL = "https://vtn.example.test"

_CONFIG = OAuthTokenManagerConfig(
    client_id="client-id",
    client_secret="client-secret",
    token_url=f"{_BASE_URL}/token",
    scopes=None,
    audience=None,
)

_EXISTING_RESOURCE_GROUP_JSON = {
    "id": "rg-1",
    "createdDateTime": "2024-01-01T00:00:00Z",
    "modificationDateTime": "2024-01-01T00:00:00Z",
    "objectType": "RESOURCE_GROUP",
    "resourceGroupName": "RG-1",
}

_DELETED_RESOURCE_GROUP_JSON = {
    "id": "rg-1",
    "createdDateTime": "2024-01-01T00:00:00Z",
    "modificationDateTime": "2024-01-01T00:00:00Z",
    "objectType": "RESOURCE_GROUP",
    "resourceGroupName": "RG-1",
}


@pytest.fixture
def interface() -> tuple[ResourceGroupsHttpInterface, MagicMock]:
    """A ResourceGroupsHttpInterface with its authenticated session replaced by a mock."""
    instance = ResourceGroupsHttpInterface(
        base_url=_BASE_URL,
        config=_CONFIG,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )
    mock_session = MagicMock()
    instance.session = mock_session
    return instance, mock_session


def test_get_resource_groups_issues_get_with_no_params_by_default(
    interface: tuple[ResourceGroupsHttpInterface, MagicMock],
) -> None:
    """get_resource_groups with no filters issues a GET with empty query params."""
    instance, mock_session = interface
    mock_session.get.return_value.json.return_value = [_EXISTING_RESOURCE_GROUP_JSON]

    result = instance.get_resource_groups()

    mock_session.get.assert_called_once_with(f"{_BASE_URL}/{BASE_PREFIX}", params={})
    mock_session.get.return_value.raise_for_status.assert_called_once()
    assert len(result) == 1
    assert result[0].id == "rg-1"


def test_get_resource_groups_merges_name_target_and_pagination_filters(
    interface: tuple[ResourceGroupsHttpInterface, MagicMock],
) -> None:
    """get_resource_groups merges resourceGroupName, target, and pagination into query params."""
    instance, mock_session = interface
    mock_session.get.return_value.json.return_value = []

    instance.get_resource_groups(
        resource_group_name="RG-1",
        target=TargetFilter(targets=["group-1"]),
        pagination=PaginationFilter(skip=0, limit=10),
    )

    mock_session.get.assert_called_once_with(
        f"{_BASE_URL}/{BASE_PREFIX}",
        params={"targets": ["group-1"], "skip": 0, "limit": 10, "resourceGroupName": "RG-1"},
    )


def test_get_resource_group_by_id_issues_get_to_id_url(
    interface: tuple[ResourceGroupsHttpInterface, MagicMock],
) -> None:
    """get_resource_group_by_id issues a GET to the /resource_groups/{id} URL."""
    instance, mock_session = interface
    mock_session.get.return_value.json.return_value = _EXISTING_RESOURCE_GROUP_JSON

    result = instance.get_resource_group_by_id("rg-1")

    mock_session.get.assert_called_once_with(f"{_BASE_URL}/{BASE_PREFIX}/rg-1")
    mock_session.get.return_value.raise_for_status.assert_called_once()
    assert result.id == "rg-1"


def test_create_resource_group_issues_post_with_serialized_body(
    interface: tuple[ResourceGroupsHttpInterface, MagicMock],
) -> None:
    """create_resource_group issues a POST with the camelCase-serialized new resource group."""
    instance, mock_session = interface
    mock_session.post.return_value.json.return_value = _EXISTING_RESOURCE_GROUP_JSON
    new_resource_group = NewResourceGroup(resource_group_name="RG-1", targets=("group-1",))

    result = instance.create_resource_group(new_resource_group)

    mock_session.post.assert_called_once_with(
        f"{_BASE_URL}/{BASE_PREFIX}",
        json=new_resource_group.model_dump(by_alias=True, mode="json"),
    )
    mock_session.post.return_value.raise_for_status.assert_called_once()
    assert result.id == "rg-1"


def test_update_resource_group_by_id_issues_put_with_serialized_body(
    interface: tuple[ResourceGroupsHttpInterface, MagicMock],
) -> None:
    """update_resource_group_by_id issues a PUT to the /resource_groups/{id} URL with the update body."""
    instance, mock_session = interface
    mock_session.put.return_value.json.return_value = _EXISTING_RESOURCE_GROUP_JSON
    update = ResourceGroupUpdate(resource_group_name="RG-1b")

    result = instance.update_resource_group_by_id("rg-1", update)

    mock_session.put.assert_called_once_with(
        f"{_BASE_URL}/{BASE_PREFIX}/rg-1",
        json=update.model_dump(by_alias=True, mode="json"),
    )
    mock_session.put.return_value.raise_for_status.assert_called_once()
    assert result.id == "rg-1"


def test_delete_resource_group_by_id_issues_delete_to_id_url(
    interface: tuple[ResourceGroupsHttpInterface, MagicMock],
) -> None:
    """delete_resource_group_by_id issues a DELETE to the /resource_groups/{id} URL."""
    instance, mock_session = interface
    mock_session.delete.return_value.json.return_value = _DELETED_RESOURCE_GROUP_JSON

    result = instance.delete_resource_group_by_id("rg-1")

    mock_session.delete.assert_called_once_with(f"{_BASE_URL}/{BASE_PREFIX}/rg-1")
    mock_session.delete.return_value.raise_for_status.assert_called_once()
    assert result.id == "rg-1"


def test_read_only_interface_has_no_create_method() -> None:
    """ResourceGroupsReadOnlyHttpInterface deliberately exposes no create method (VEN scope)."""
    read_only = ResourceGroupsReadOnlyHttpInterface(
        base_url=_BASE_URL,
        config=_CONFIG,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )
    assert not hasattr(read_only, "create_resource_group")
