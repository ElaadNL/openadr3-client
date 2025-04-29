"""Contains tests for the vens VTN module."""

import pytest
from requests import HTTPError
from openadr3_client._vtn.http.vens import VensHttpInterface
from openadr3_client.models.ven.ven import ExistingVen, NewVen
from openadr3_client.models.ven.resource import ExistingResource, NewResource
from openadr3_client.models.common.attribute import Attribute
from openadr3_client.models.common.target import Target
from tests.conftest import IntegrationTestVTNClient

from datetime import UTC, datetime, timezone


def test_get_vens_no_vens_in_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting vens in a VTN without any vens returns an empty list."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    response = interface.get_vens(ven_name=None, target=None, pagination=None)

    assert len(response) == 0, "no vens should be stored in VTN."


def test_get_ven_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a ven by ID in a VTN with no such ven raises an exception."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_ven_by_id(ven_id="fake-ven-id")


def test_delete_ven_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a ven by ID in a VTN with no such ven raises a 404 error."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_ven_by_id(ven_id="fake-ven-id")


def test_update_ven_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a ven by ID in a VTN with no such ven raises a 404 error."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    
    with pytest.raises(HTTPError, match="404 Client Error"):
        tz_aware_dt = datetime.now(tz=timezone.utc)
        interface.update_ven_by_id(
            ven_id="fake-ven-id",
            updated_ven=ExistingVen(
                id="fake-ven-id",
                ven_name="test-ven",
                created_date_time=tz_aware_dt,
                modification_date_time=tz_aware_dt,
                attributes=(
                    Attribute(type="test-attribute", values=("test-value",)),
                ),
                targets=(
                    Target(type="test-target", values=("test-value",)),
                )
            ))


def test_create_ven(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a ven in a VTN works correctly."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    ven = NewVen(
        id=None,
        ven_name="test-ven",
        attributes=(
            Attribute(type="test-attribute", values=("test-value",)),
        ),
        targets=(
            Target(type="test-target", values=("test-value",)),
        )
    )

    response = interface.create_ven(new_ven=ven)
    
    assert response.id is not None, "ven should be created successfully."
    assert response.ven_name == "test-ven", "ven name should match"
    assert response.attributes is not None and len(response.attributes) == 1, "attributes should match"
    assert response.targets is not None and len(response.targets) == 1, "targets should match"


def test_get_ven_resources_no_resources(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting resources for a ven without any resources returns an empty list."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    response = interface.get_ven_resources(
        ven_id="fake-ven-id",
        resource_name=None,
        target=None,
        pagination=None,
    )

    assert len(response) == 0, "no resources should be stored for the ven."


def test_get_ven_resource_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a resource by ID for a ven with no such resource raises an exception."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_ven_resource_by_id(ven_id="fake-ven-id", resource_id="fake-resource-id")


def test_delete_ven_resource_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a resource by ID for a ven with no such resource raises a 404 error."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_ven_resource_by_id(ven_id="fake-ven-id", resource_id="fake-resource-id")


def test_update_ven_resource_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a resource by ID for a ven with no such resource raises a 404 error."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # First create a ven
    ven = NewVen(
        id=None,
        ven_name="test-ven",
        attributes=(
            Attribute(type="test-attribute", values=("test-value",)),
        ),
        targets=(
            Target(type="test-target", values=("test-value",)),
        )
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"
    
    with pytest.raises(HTTPError, match="404 Client Error"):
        tz_aware_dt = datetime.now(tz=timezone.utc)
        interface.update_ven_resource_by_id(
            ven_id="fake-ven-id",
            resource_id="fake-resource-id",
            updated_resource=ExistingResource(
                id="fake-resource-id",
                resource_name="test-resource",
                venID="fake-ven-id",
                created_date_time=tz_aware_dt,
                modification_date_time=tz_aware_dt,
                attributes=(
                    Attribute(type="test-attribute", values=("test-value",)),
                ),
                targets=(
                    Target(type="test-target", values=("test-value",)),
                )
            ))
        
    interface.delete_ven_by_id(ven_id=created_ven.id)


def test_create_ven_resource(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a resource for a ven in a VTN works correctly."""
    interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # First create a ven
    ven = NewVen(
        id=None,
        ven_name="test-ven",
        attributes=(
            Attribute(type="test-attribute", values=("test-value",)),
        ),
        targets=(
            Target(type="test-target", values=("test-value",)),
        )
    )
    created_ven = interface.create_ven(new_ven=ven)
    assert created_ven.id is not None, "ven should be created successfully"

    # Now create a resource for the ven
    resource = NewResource(
        id=None,
        resource_name="test-resource",
        venID=created_ven.id,
        attributes=(
            Attribute(type="test-attribute", values=("test-value",)),
        ),
        targets=(
            Target(type="test-target", values=("test-value",)),
        )
    )

    response = interface.create_ven_resource(ven_id=created_ven.id, new_resource=resource)

    interface.delete_ven_resource_by_id(ven_id=created_ven.id, resource_id=response.id)
    interface.delete_ven_by_id(ven_id=created_ven.id)
    
    assert response.id is not None, "resource should be created successfully."
    assert response.resource_name == "test-resource", "resource name should match"
    assert response.ven_id == created_ven.id, "ven id should match"
    assert response.attributes is not None and len(response.attributes) == 1, "attributes should match"
    assert response.targets is not None and len(response.targets) == 1, "targets should match" 
    