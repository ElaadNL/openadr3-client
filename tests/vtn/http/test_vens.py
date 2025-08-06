"""Contains tests for the vens VTN module."""

from datetime import UTC, datetime

import pytest
from requests import HTTPError

from openadr3_client._vtn.http.vens import VensHttpInterface
from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.common.attribute import Attribute
from openadr3_client.models.common.target import Target
from openadr3_client.models.ven.resource import ExistingResource, NewResource, ResourceUpdate
from openadr3_client.models.ven.ven import ExistingVen, NewVen, VenUpdate
from tests.conftest import IntegrationTestVTNClient


def test_get_vens_no_vens_in_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting vens in a VTN without any vens returns an empty list."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    response = interface.get_vens(ven_name=None, target=None, pagination=None)

    assert len(response) == 0, "no vens should be stored in VTN."


def test_get_ven_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a ven by ID in a VTN with no such ven raises an exception."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_ven_by_id(ven_id="fake-ven-id")


def test_delete_ven_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a ven by ID in a VTN with no such ven raises a 404 error."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_ven_by_id(ven_id="fake-ven-id")


def test_update_ven_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a ven by ID in a VTN with no such ven raises a 404 error."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    tz_aware_dt = datetime.now(tz=UTC)
    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.update_ven_by_id(
            ven_id="fake-ven-id",
            updated_ven=ExistingVen(
                id="fake-ven-id",
                ven_name="test-ven",
                created_date_time=tz_aware_dt,
                modification_date_time=tz_aware_dt,
                attributes=(Attribute(type="test-attribute", values=("test-value",)),),
                targets=(Target(type="test-target", values=("test-value",)),),
            ),
        )


def test_create_ven(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a ven in a VTN works correctly."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    ven = NewVen(
        ven_name="test-ven",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )

    response = interface.create_ven(new_ven=ven)

    assert response.id is not None, "ven should be created successfully."
    assert response.ven_name == "test-ven", "ven name should match"
    assert response.attributes is not None and len(response.attributes) == 1, "attributes should match"
    assert response.targets is not None and len(response.targets) == 1, "targets should match"

    interface.delete_ven_by_id(ven_id=response.id)


def test_get_ven_resources_no_resources(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting resources for a ven without any resources returns an empty list."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    response = interface.get_ven_resources(
        ven_id="fake-ven-id",
        resource_name=None,
        target=None,
        pagination=None,
    )

    assert len(response) == 0, "no resources should be stored for the ven."


def test_get_ven_resource_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a resource by ID for a ven with no such resource raises an exception."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )
    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_ven_resource_by_id(ven_id="fake-ven-id", resource_id="fake-resource-id")


def test_delete_ven_resource_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a resource by ID for a ven with no such resource raises a 404 error."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_ven_resource_by_id(ven_id="fake-ven-id", resource_id="fake-resource-id")


def test_delete_ven_resource_by_id(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a resource by ID for a ven works when the resource exists."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # First create a ven
    ven = NewVen(
        ven_name="test-ven-with-resource-to-delete",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"
    assert created_ven.ven_name == "test-ven-with-resource-to-delete", "ven name should match"
    assert created_ven.attributes is not None and len(created_ven.attributes) == 1, "attribute count should match"
    assert created_ven.attributes[0].type == "test-attribute", "attribute type should match"
    assert created_ven.attributes[0].values == ("test-value",), "attribute values should match"
    assert created_ven.targets is not None and len(created_ven.targets) == 1, "target count should match"
    assert created_ven.targets[0].type == "test-target", "target type should match"
    assert created_ven.targets[0].values == ("test-value",), "target values should match"

    try:
        resource = NewResource(
            resource_name="test-resource",
            venID=created_ven.id,
            attributes=(Attribute(type="test-attribute", values=("test-value",)),),
            targets=(Target(type="test-target", values=("test-value",)),),
        )
        created_resource = interface.create_ven_resource(ven_id=created_ven.id, new_resource=resource)
        assert created_resource.id is not None, "resource should be created successfully"

        deleted_resource = interface.delete_ven_resource_by_id(ven_id=created_ven.id, resource_id=created_resource.id)
        assert deleted_resource.id == created_resource.id, "resource id should match"
        assert deleted_resource.resource_name == "test-resource", "resource name should match"
        assert deleted_resource.ven_id == created_resource.ven_id, "ven id should match"
        assert deleted_resource.created_date_time == created_resource.created_date_time, (
            "created date time should match"
        )
        assert deleted_resource.modification_date_time == created_resource.modification_date_time, (
            "modification date time should match"
        )
        assert deleted_resource.attributes is not None and len(deleted_resource.attributes) == 1, (
            "attribute count should match"
        )
        assert deleted_resource.attributes[0].type == "test-attribute", "attribute type should match"
        assert deleted_resource.attributes[0].values == ("test-value",), "attribute values should match"
        assert deleted_resource.targets is not None and len(deleted_resource.targets) == 1, "target count should match"
        assert deleted_resource.targets[0].type == "test-target", "target type should match"
        assert deleted_resource.targets[0].values == ("test-value",), "target values should match"

        # Verify the resource is deleted
        with pytest.raises(HTTPError, match="404 Client Error"):
            _ = interface.get_ven_resource_by_id(ven_id=created_ven.id, resource_id=created_resource.id)
    finally:
        interface.delete_ven_by_id(ven_id=created_ven.id)


def test_update_ven_resource_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a resource by ID for a ven with no such resource raises a 404 error."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # First create a ven
    ven = NewVen(
        ven_name="test-ven-with-with-non-existent-resource",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"
    assert created_ven.ven_name == "test-ven-with-with-non-existent-resource", "ven name should match"
    assert created_ven.attributes is not None and len(created_ven.attributes) == 1, "attribute count should match"
    assert created_ven.attributes[0].type == "test-attribute", "attribute type should match"
    assert created_ven.attributes[0].values == ("test-value",), "attribute values should match"
    assert created_ven.targets is not None and len(created_ven.targets) == 1, "target count should match"
    assert created_ven.targets[0].type == "test-target", "target type should match"
    assert created_ven.targets[0].values == ("test-value",), "target values should match"

    try:
        tz_aware_dt = datetime.now(tz=UTC)
        with pytest.raises(HTTPError, match="404 Client Error"):
            interface.update_ven_resource_by_id(
                ven_id=created_ven.id,
                resource_id="does-not-exist",
                updated_resource=ExistingResource(
                    id="does-not-exist",
                    resource_name="test-resource",
                    venID=created_ven.id,
                    created_date_time=tz_aware_dt,
                    modification_date_time=tz_aware_dt,
                    attributes=(Attribute(type="test-attribute", values=("test-value",)),),
                    targets=(Target(type="test-target", values=("test-value",)),),
                ),
            )
    finally:
        interface.delete_ven_by_id(ven_id=created_ven.id)


def test_update_ven_resource_by_id(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a resource by ID for a ven works when the resource exists."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # First create a ven
    ven = NewVen(
        ven_name="test-ven-with-resource-to-update",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"

    try:
        # Now create a resource for the ven
        resource = NewResource(
            resource_name="test-resource",
            venID=created_ven.id,
            attributes=(Attribute(type="test-attribute", values=("test-value",)),),
            targets=(Target(type="test-target", values=("test-value",)),),
        )

        created_resource = interface.create_ven_resource(ven_id=created_ven.id, new_resource=resource)
        assert created_resource.id is not None, "resource should be created successfully"

        resource_update = ResourceUpdate(
            resource_name="test-resource-updated-name",
            attributes=(Attribute(type="test-attribute-updated", values=("test-value-updated",)),),
            targets=(Target(type="test-target-updated", values=("test-value-updated",)),),
        )

        updated_resource = interface.update_ven_resource_by_id(
            ven_id=created_ven.id,
            resource_id=created_resource.id,
            updated_resource=created_resource.update(resource_update),
        )

        interface.delete_ven_resource_by_id(ven_id=created_ven.id, resource_id=created_resource.id)

        assert updated_resource.id == created_resource.id, "resource id should match"
        assert updated_resource.resource_name == "test-resource-updated-name", "resource name should match"
        assert updated_resource.ven_id == created_resource.ven_id, "ven id should match"
        assert updated_resource.created_date_time == created_resource.created_date_time, (
            "created date time should match"
        )
        assert updated_resource.modification_date_time != created_resource.modification_date_time, (
            "modification date time should not match"
        )
        assert updated_resource.attributes is not None and len(updated_resource.attributes) == 1, (
            "attribute count should match"
        )
        assert updated_resource.attributes[0].type == "test-attribute-updated", "attribute type should match"
        assert updated_resource.attributes[0].values == ("test-value-updated",), "attribute values should match"
        assert updated_resource.targets is not None and len(updated_resource.targets) == 1, "target count should match"
        assert updated_resource.targets[0].type == "test-target-updated", "target type should match"
        assert updated_resource.targets[0].values == ("test-value-updated",), "target values should match"

    finally:
        interface.delete_ven_by_id(ven_id=created_ven.id)


def test_create_ven_resource(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a resource for a ven in a VTN works correctly."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # First create a ven
    ven = NewVen(
        ven_name="test-ven-with-resource",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"

    # Now create a resource for the ven
    resource = NewResource(
        resource_name="test-resource",
        venID=created_ven.id,
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )

    response = interface.create_ven_resource(ven_id=created_ven.id, new_resource=resource)

    interface.delete_ven_resource_by_id(ven_id=created_ven.id, resource_id=response.id)
    interface.delete_ven_by_id(ven_id=created_ven.id)

    assert response.id is not None, "resource should be created successfully."
    assert response.resource_name == "test-resource", "resource name should match"
    assert response.ven_id == created_ven.id, "ven id should match"
    assert response.attributes is not None and len(response.attributes) == 1, "attributes should match"
    assert response.targets is not None and len(response.targets) == 1, "targets should match"


def test_create_ven_duplicate_name(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a ven with a duplicate name raises a conflict error."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # First create a ven
    ven = NewVen(
        ven_name="test-ven-duplicate",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"

    ven2 = NewVen(
        ven_name="test-ven-duplicate",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )

    try:
        # Try to create another ven with the same name
        with pytest.raises(HTTPError, match="409 Client Error"):
            _ = interface.create_ven(new_ven=ven2)
    finally:
        interface.delete_ven_by_id(ven_id=created_ven.id)


def test_get_vens_with_parameters(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate getting vens with various parameter combinations."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # Create two vens with different names and targets
    ven1 = NewVen(
        ven_name="test-ven-1",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target-1", values=("test-value-1",)),),
    )
    ven2 = NewVen(
        ven_name="test-ven-2",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target-2", values=("test-value-2",)),),
    )
    created_ven1 = interface.create_ven(new_ven=ven1)
    created_ven2 = interface.create_ven(new_ven=ven2)

    try:
        # Test getting all vens
        all_vens = interface.get_vens(ven_name=None, target=None, pagination=None)
        assert len(all_vens) == 2, "Should return both vens"

        # Test getting vens by name
        ven1_by_name = interface.get_vens(ven_name="test-ven-1", target=None, pagination=None)
        assert len(ven1_by_name) == 1, "Should return one ven"
        assert ven1_by_name[0].ven_name == "test-ven-1", "Should return the correct ven"

        # Test getting vens by target
        target_filter = TargetFilter(target_type="test-target-1", target_values=["test-value-1"])
        ven1_by_target = interface.get_vens(ven_name=None, target=target_filter, pagination=None)
        assert len(ven1_by_target) == 1, "Should return one ven"
        assert ven1_by_target[0].ven_name == "test-ven-1", "Should return the correct ven"

        # Test pagination
        pagination_filter = PaginationFilter(skip=0, limit=1)
        paginated_vens = interface.get_vens(ven_name=None, target=None, pagination=pagination_filter)
        assert len(paginated_vens) == 1, "Should return one ven due to pagination"
    finally:
        interface.delete_ven_by_id(ven_id=created_ven1.id)
        interface.delete_ven_by_id(ven_id=created_ven2.id)


def test_delete_ven(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate deleting a ven that exists."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # Create a ven to delete
    ven = NewVen(
        ven_name="test-ven-to-delete",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"

    # Delete the ven
    deleted_ven = interface.delete_ven_by_id(ven_id=created_ven.id)

    # Verify returned ven
    assert deleted_ven.id == created_ven.id, "ven id should match"
    assert deleted_ven.ven_name == created_ven.ven_name, "ven name should match"
    assert deleted_ven.created_date_time == created_ven.created_date_time, "created date time should match"
    assert deleted_ven.modification_date_time == created_ven.modification_date_time, (
        "modification date time should match"
    )
    assert deleted_ven.attributes is not None, "attributes should not be None"
    assert deleted_ven.targets is not None, "targets should not be None"
    assert len(deleted_ven.attributes) == 1, "attributes should have one attribute"
    assert len(deleted_ven.targets) == 1, "targets should have one target"
    assert deleted_ven.attributes[0].type == "test-attribute", "attribute type should match"
    assert deleted_ven.attributes[0].values == ("test-value",), "attribute values should match"
    assert deleted_ven.targets[0].type == "test-target", "target type should match"
    assert deleted_ven.targets[0].values == ("test-value",), "target values should match"

    # Verify the ven is deleted
    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_ven_by_id(ven_id=created_ven.id)


def test_update_ven(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate updating a ven that exists."""
    interface = VensHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # Create a ven to update
    ven = NewVen(
        ven_name="test-ven-to-update",
        attributes=(Attribute(type="test-attribute", values=("test-value",)),),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"

    try:
        # Update the ven
        ven_update = VenUpdate(
            ven_name="test-ven-updated",
            attributes=(Attribute(type="test-attribute-updated", values=("test-value-updated",)),),
            targets=(Target(type="test-target-updated", values=("test-value-updated",)),),
        )

        updated_ven = interface.update_ven_by_id(ven_id=created_ven.id, updated_ven=created_ven.update(ven_update))

        # Verify the update
        assert updated_ven.ven_name == "test-ven-updated", "ven name should be updated"
        assert updated_ven.attributes is not None, "attributes should not be None"
        assert updated_ven.created_date_time == created_ven.created_date_time, "created date time should match"
        assert updated_ven.modification_date_time != created_ven.modification_date_time, (
            "modification date time should not match"
        )
        assert len(updated_ven.attributes) > 0, "attributes should not be empty"
        assert updated_ven.attributes[0].type == "test-attribute-updated", "attribute type should be updated"
        assert updated_ven.attributes[0].values == ("test-value-updated",), "attribute values should be updated"
        assert updated_ven.targets is not None, "targets should not be None"
        assert len(updated_ven.targets) > 0, "targets should not be empty"
        assert updated_ven.targets[0].type == "test-target-updated", "target type should be updated"
        assert updated_ven.targets[0].values == ("test-value-updated",), "target values should be updated"
    finally:
        interface.delete_ven_by_id(ven_id=created_ven.id)
