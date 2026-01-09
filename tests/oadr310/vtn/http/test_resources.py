"""Contains tests for the resources VTN module."""

import pytest
from requests import HTTPError

from openadr3_client._models.common.attribute import Attribute
from openadr3_client.oadr310._vtn.http.resources import ResourcesHttpInterface
from openadr3_client.oadr310.models.resource.resource import ResourceUpdateBlRequest
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import resource_for_ven, ven_with_targets


def test_get_ven_resources_no_resources(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that getting resources for a ven without any resources returns an empty list."""
    interface = ResourcesHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    resources = interface.get_resources()

    assert len(resources) == 0, "no resources should be stored for the ven."


def test_get_ven_resource_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that getting a resource by ID for a ven with no such resource raises an exception."""
    interface = ResourcesHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_resource_by_id(resource_id="fake-resource-id")


def test_delete_ven_resource_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that deleting a resource by ID for a ven with no such resource raises a 404 error."""
    interface = ResourcesHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_resource_by_id(resource_id="fake-resource-id")


def test_delete_ven_resource_by_id(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that deleting a resource by ID for a ven works when the resource exists."""
    interface = ResourcesHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with (
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            ven_name="test-ven-with-resource-to-delete",
            client_id_of_ven="client-id-of-ven-with-resource-to-delete",
            targets=("test-target",),
        ) as created_ven,
        resource_for_ven(
            vtn_client=vtn_openadr_310_bl_token,
            ven_id=created_ven.id,
            resource_name="test-resource",
            client_id_of_resource=created_ven.client_id,
            attributes=(Attribute(type="test-attribute", values=("test-value",)),),
            targets=("test-target",),
        ) as created_resource,
    ):
        deleted_resource = interface.delete_resource_by_id(resource_id=created_resource.id)

        assert deleted_resource.id == created_resource.id, "resource id should match"
        assert deleted_resource.resource_name == created_resource.resource_name, "resource name should match"
        assert deleted_resource.ven_id == created_resource.ven_id, "ven id should match"
        assert deleted_resource.created_date_time == created_resource.created_date_time, "created date time should match"
        assert deleted_resource.modification_date_time == created_resource.modification_date_time, "modification date time should match"
        assert deleted_resource.attributes is not None and len(deleted_resource.attributes) == 1, "attribute count should match"
        assert deleted_resource.attributes[0].type == "test-attribute", "attribute type should match"
        assert deleted_resource.attributes[0].values == ("test-value",), "attribute values should match"
        assert deleted_resource.targets is not None and len(deleted_resource.targets) == 1, "target count should match"
        assert deleted_resource.targets[0] == "test-target", "target should match"

        with pytest.raises(HTTPError, match="404 Client Error"):
            _ = interface.get_resource_by_id(resource_id=created_resource.id)


def test_update_ven_resource_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that updating a resource by ID for a ven with no such resource raises a 404 error."""
    interface = ResourcesHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with (
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            ven_name="test-ven-with-non-existent-resource",
            client_id_of_ven="client-id-of-ven-with-non-existent-resource",
        ) as created_ven,
        pytest.raises(HTTPError, match="404 Client Error"),
    ):
        interface.update_resource_by_id(
            resource_id="does-not-exist",
            updated_resource=ResourceUpdateBlRequest(
                resource_name="test-resource",
                venID=created_ven.id,
                attributes=(Attribute(type="test-attribute", values=("test-value",)),),
                clientID=created_ven.client_id,
                targets=("test-target",),
            ),
        )


def test_update_ven_resource_by_id(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that updating a resource by ID for a ven works when the resource exists."""
    interface = ResourcesHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with (
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            ven_name="test-ven-with-resource-to-update",
            client_id_of_ven="client-id-of-ven-with-resource-to-update",
            targets=("test-target",),
        ) as created_ven,
        resource_for_ven(
            vtn_client=vtn_openadr_310_bl_token,
            ven_id=created_ven.id,
            resource_name="test-resource",
            client_id_of_resource=created_ven.client_id,
            attributes=(Attribute(type="test-attribute", values=("test-value",)),),
            targets=("test-target",),
        ) as created_resource,
    ):
        resource_update = ResourceUpdateBlRequest(
            resource_name="test-resource-updated-name",
            attributes=(Attribute(type="test-attribute-updated", values=("test-value-updated",)),),
            clientID=created_resource.client_id,
            targets=("test-target-updated",),
            venID=created_resource.ven_id,
        )

        updated_resource = interface.update_resource_by_id(
            resource_id=created_resource.id,
            updated_resource=resource_update,
        )

        assert updated_resource.id == created_resource.id, "resource id should match"
        assert updated_resource.resource_name == "test-resource-updated-name", "resource name should match"
        assert updated_resource.ven_id == created_resource.ven_id, "ven id should match"
        assert updated_resource.created_date_time == created_resource.created_date_time, "created date time should match"
        assert updated_resource.attributes is not None and len(updated_resource.attributes) == 1, "attribute count should match"
        assert updated_resource.attributes[0].type == "test-attribute-updated", "attribute type should match"
        assert updated_resource.attributes[0].values == ("test-value-updated",), "attribute values should match"
        assert updated_resource.targets is not None and len(updated_resource.targets) == 1, "target count should match"
        assert updated_resource.targets[0] == "test-target-updated", "target should match"


def test_create_ven_resource(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that creating a resource for a ven in a VTN works correctly."""
    with (
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            ven_name="test-ven-with-resource",
            client_id_of_ven="client-id-of-ven-with-resource",
            targets=("test-target",),
        ) as created_ven,
        resource_for_ven(
            vtn_client=vtn_openadr_310_bl_token,
            ven_id=created_ven.id,
            resource_name="test-resource",
            client_id_of_resource=created_ven.client_id,
            attributes=(Attribute(type="test-attribute", values=("test-value",)),),
            targets=("test-target",),
        ) as created_resource,
    ):
        assert created_resource.id is not None, "resource should be created successfully."
        assert created_resource.resource_name == "test-resource", "resource name should match"
        assert created_resource.ven_id == created_ven.id, "ven id should match"
        assert created_resource.attributes is not None and len(created_resource.attributes) == 1, "attributes should match"
        assert created_resource.targets is not None and len(created_resource.targets) == 1, "targets should match"
