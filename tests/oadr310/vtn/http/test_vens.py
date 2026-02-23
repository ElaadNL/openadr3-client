# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains tests for the vens VTN module."""

import pytest
from requests import HTTPError

from openadr3_client._models.common.attribute import Attribute
from openadr3_client.oadr310._vtn.http.vens import VensHttpInterface
from openadr3_client.oadr310._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.oadr310.models.ven.ven import VenUpdateBlRequest, VenUpdateVenRequest
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import ven_created_by_ven, ven_with_targets


def test_bl_get_vens_no_vens_in_vtn(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting vens in a VTN without any vens returns an empty list."""
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    response = interface.get_vens(ven_name=None, target=None, pagination=None)

    assert len(response) == 0, "no vens should be stored in VTN."


def test_ven_get_vens_no_vens_in_vtn(vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting vens in a VTN without any vens returns an empty list."""
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    response = interface.get_vens(ven_name=None, target=None, pagination=None)

    assert len(response) == 0, "no vens should be stored in VTN."


def test_get_ven_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a ven by ID in a VTN with no such ven raises an exception."""
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_ven_by_id(ven_id="fake-ven-id")


def test_delete_ven_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a ven by ID in a VTN with no such ven raises a 404 error."""
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_ven_by_id(ven_id="fake-ven-id")


def test_update_ven_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a ven by ID in a VTN with no such ven raises a 404 error."""
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.update_ven_by_id(
            ven_id="fake-ven-id",
            updated_ven=VenUpdateBlRequest(
                ven_name="test-ven",
                attributes=(Attribute(type="test-attribute", values=("test-value",)),),
                targets=("test-value",),
                clientID="non-existent-client-id",
            ),
        )


def test_create_ven_bl(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a ven in a VTN works correctly for a BL."""
    ven_name = "test-ven-create-bl"
    ven_targets_assigned_by_bl = ("target-1",)

    with ven_with_targets(vtn_client=vtn_openadr_310_bl_token, ven_name=ven_name, client_id_of_ven="a-random-client-id", targets=ven_targets_assigned_by_bl) as created_ven:
        assert created_ven.id is not None, "ven should be created successfully."
        assert created_ven.ven_name == ven_name, "ven name should match"
        assert created_ven.attributes is None, "attributes should match"
        assert created_ven.targets == ven_targets_assigned_by_bl, "targets should match"


def test_create_ven_ven(vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a ven in a VTN works correctly for a BL."""
    ven_name = "ven-created-by-ven"

    with ven_created_by_ven(vtn_client=vtn_openadr_310_ven_token, ven_name=ven_name) as created_ven:
        assert created_ven.id is not None, "ven should be created successfully."
        assert created_ven.ven_name == ven_name, "ven name should match"
        assert created_ven.attributes is None, "attributes should match"
        assert created_ven.targets == (), "targets should match"


def test_create_ven_duplicate_name(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a ven with a duplicate name raises a conflict error."""
    ven_name = "ven-name-duplicate"

    with (
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            ven_name=ven_name,
            client_id_of_ven="a-random-client-id-2",
        ),
        pytest.raises(HTTPError, match="409 Client Error"),
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            ven_name=ven_name,
            client_id_of_ven="a-random-client-id-2",
        ),
    ):
        pytest.fail("VEN with duplicate name should not be created!")


def test_get_all_vens(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """
    Test that validates a BL can retrieve VENs with pagination.

    Args:
        vtn_openadr_310_bl_token (IntegrationTestVTNClient): The BL vtn client configuration.

    """
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    ven_name = "my-ven-name-get-all"
    ven_name_2 = "my-ven-name-get-all-2"

    with (
        ven_with_targets(vtn_openadr_310_bl_token, ven_name=ven_name, client_id_of_ven="a-client-id-for-test") as ven1,
        ven_with_targets(vtn_openadr_310_bl_token, ven_name=ven_name_2, client_id_of_ven="a-client-id-for-test-2") as ven2,
    ):
        vens_paginated = interface.get_vens(ven_name=None, target=None, pagination=None)
        assert len(vens_paginated) == 2, "Should return two vens"
        assert vens_paginated in {(ven1, ven2), (ven2, ven1)}, "Should return both vens in any order"


def test_get_vens_paginated(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """
    Test that validates a BL can retrieve VENs with pagination.

    Args:
        vtn_openadr_310_bl_token (IntegrationTestVTNClient): The BL vtn client configuration.

    """
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    ven_name = "my-ven-name-paginated"
    ven_name_2 = "my-ven-name-paginated-2"

    with (
        ven_with_targets(vtn_openadr_310_bl_token, ven_name=ven_name, client_id_of_ven="a-client-id-for-paginated-test"),
        ven_with_targets(vtn_openadr_310_bl_token, ven_name=ven_name_2, client_id_of_ven="a-client-id-for-paginated-test-2"),
    ):
        pagination_filter = PaginationFilter(skip=1, limit=5)
        vens_paginated = interface.get_vens(ven_name=None, target=None, pagination=pagination_filter)
        assert len(vens_paginated) == 1, "Should return one ven"


def test_get_vens_by_target_bl(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """
    Test that validates a BL can retrieve VENs with specific targets.

    Args:
        vtn_openadr_310_bl_token (IntegrationTestVTNClient): The BL vtn client configuration.

    """
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    ven_name = "my-ven-name-target-bl"
    ven_targets = ("test-target-2",)

    with ven_with_targets(vtn_client=vtn_openadr_310_bl_token, ven_name=ven_name, client_id_of_ven="a-client-id-for-target-bl-test", targets=ven_targets) as created_ven:
        # Test getting vens by target
        target_filter = TargetFilter(targets=list(ven_targets))
        vens_by_target = interface.get_vens(ven_name=None, target=target_filter, pagination=None)
        assert len(vens_by_target) == 1, "Should return one ven"
        assert vens_by_target[0] == created_ven, "Should return the correct ven"


def test_get_vens_ven_no_associated_ven_object(vtn_openadr_310_bl_token: IntegrationTestVTNClient, vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """
    Test that validates a VEN cannot retrieve others VENS object not associated with its client.

    Args:
        vtn_openadr_310_bl_token (IntegrationTestVTNClient): The BL vtn client configuration.
        vtn_openadr_310_ven_token (IntegrationTestVTNClient): The ven vtn client configuration.

    """
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    ven_name = "my-ven-name-target-ven-not-allowed"

    with ven_with_targets(vtn_client=vtn_openadr_310_bl_token, ven_name=ven_name, client_id_of_ven="test-client-id-not-associated-with-ven"):
        vens_by_target = interface.get_vens(ven_name=None, target=None, pagination=None)
        assert len(vens_by_target) == 0, "Should return no vens"


def test_get_vens_ven_can_only_see_associated_ven_object(vtn_openadr_310_bl_token: IntegrationTestVTNClient, vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """
    Test that validates a VEN can only retrieve its own VEN object associated with the client.

    Args:
        vtn_openadr_310_bl_token (IntegrationTestVTNClient): The BL vtn client configuration.
        vtn_openadr_310_ven_token (IntegrationTestVTNClient): The ven vtn client configuration.

    """
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    ven_name = "my-ven-name-target-ven-allowed"
    ven_name_2 = "my-ven-name-target-ven-allowed-2"
    with (
        ven_with_targets(
            vtn_openadr_310_bl_token,
            ven_name=ven_name,
            client_id_of_ven=vtn_openadr_310_ven_token.openadr_client_id,
            targets=("test-target-1",),
        ) as my_ven,
        ven_with_targets(vtn_openadr_310_bl_token, ven_name=ven_name_2, client_id_of_ven="a-client-id-for-testting"),
    ):
        vens_visible_to_ven = interface.get_vens(ven_name=None, target=None, pagination=None)
        assert len(vens_visible_to_ven) == 1, "Should return single ven visible to client"
        assert vens_visible_to_ven[0] == my_ven, "Should return my ven object"


def test_delete_ven_bl(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate deleting a ven that exists works for a BL."""
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    with ven_with_targets(vtn_openadr_310_bl_token, ven_name="ven-name-to-delete", client_id_of_ven="client-id-of-ven-to-delete", targets=("test-target-1",)) as ven_to_delete:
        # Delete the ven
        deleted_ven = interface.delete_ven_by_id(ven_id=ven_to_delete.id)

        # Verify returned ven
        assert deleted_ven.id == ven_to_delete.id

        # Verify the ven is deleted
        with pytest.raises(HTTPError, match="404 Client Error"):
            _ = interface.get_ven_by_id(ven_id=ven_to_delete.id)


def test_delete_associated_ven_by_ven(vtn_openadr_310_bl_token: IntegrationTestVTNClient, vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """
    Test that validates a VEN can only delete its own VEN object associated with the client.

    Args:
        vtn_openadr_310_bl_token (IntegrationTestVTNClient): The BL vtn client configuration.
        vtn_openadr_310_ven_token (IntegrationTestVTNClient): The ven vtn client configuration.

    """
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    ven_name = "my-ven-name-target-ven-to-delete"
    ven_name_2 = "my-ven-name-target-ven-not-owned"
    with (
        ven_with_targets(
            vtn_openadr_310_bl_token,
            ven_name=ven_name,
            client_id_of_ven=vtn_openadr_310_ven_token.openadr_client_id,
            targets=("test-target-1",),
        ) as my_ven,
        ven_with_targets(vtn_openadr_310_bl_token, ven_name=ven_name_2, client_id_of_ven="a-client-id-for-test"),
    ):
        # Delete the ven associated with the client.
        deleted_ven = interface.delete_ven_by_id(ven_id=my_ven.id)

        # Verify returned ven
        assert deleted_ven.id == my_ven.id

        # Verify the ven is deleted
        with pytest.raises(HTTPError, match="404 Client Error"):
            _ = interface.get_ven_by_id(ven_id=my_ven.id)


def test_update_ven_bl(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate updating a ven that exists works for a BL."""
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    with ven_with_targets(
        vtn_openadr_310_bl_token, ven_name="ven-name-to-update-ven", client_id_of_ven="client-id-of-ven-to-update", targets=("test-target-1",)
    ) as ven_to_update:
        new_targets = ("test-target-updated",)

        update = VenUpdateBlRequest(ven_name="new-ven-name-updated-by-bl", targets=new_targets, clientID="client-id-of-ven-to-update")
        # update the ven
        updated_ven = interface.update_ven_by_id(ven_id=ven_to_update.id, updated_ven=update)

        assert updated_ven.id == ven_to_update.id, "ven ID for updated ven should match original"
        assert updated_ven.ven_name != ven_to_update.ven_name, "Ven name should have been updated"
        assert updated_ven.targets == new_targets, "Ven targets should have been updated"


def test_update_associated_ven_by_ven(vtn_openadr_310_bl_token: IntegrationTestVTNClient, vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """
    Test that validates a VEN can only update its own VEN object associated with the client.

    Args:
        vtn_openadr_310_bl_token (IntegrationTestVTNClient): The BL vtn client configuration.
        vtn_openadr_310_ven_token (IntegrationTestVTNClient): The ven vtn client configuration.

    """
    interface = VensHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,
        allow_insecure_http=True,
    )

    ven_name = "my-ven-name-target-ven-to-update"
    ven_name_2 = "my-ven-name-target-ven-not-owned-for-update"
    with (
        ven_with_targets(
            vtn_openadr_310_bl_token,
            ven_name=ven_name,
            client_id_of_ven=vtn_openadr_310_ven_token.openadr_client_id,
            targets=("test-target-1",),
        ) as my_ven,
        ven_with_targets(vtn_openadr_310_bl_token, ven_name=ven_name_2, client_id_of_ven="a-client-id-for-test"),
    ):
        update = VenUpdateVenRequest(ven_name="new-ven-name-updated-by-ven")
        # Update the ven associated with the client.
        updated_ven = interface.update_ven_by_id(ven_id=my_ven.id, updated_ven=update)

        assert updated_ven.id == my_ven.id, "ven ID for updated ven should match original"
        assert updated_ven.ven_name != my_ven.ven_name, "Ven name should have been updated"
