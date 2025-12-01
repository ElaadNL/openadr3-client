"""Implements the communication with the vens interface of an OpenADR 3 VTN."""

from pydantic.type_adapter import TypeAdapter

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client._vtn.oadr310.http.http_interface import AuthenticatedHttpInterface
from openadr3_client._vtn.oadr310.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client._vtn.oadr310.interfaces.resources import ReadOnlyResourcesInterface, ReadWriteResourceInterface, WriteOnlyResourcesInterface
from openadr3_client.logging import logger
from openadr3_client.models.oadr310.resource.resource import DeletedResource, ExistingResource, NewResource

base_prefix = "resources"


class ResourcesReadOnlyHttpInterface(ReadOnlyResourcesInterface, AuthenticatedHttpInterface):
    """Implements the read communication with the resources HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, config=config, verify_tls_certificate=verify_tls_certificate)

    def get_resources(
        self,
        ven_id: str,
        resource_name: str | None,
        target: TargetFilter | None,
        pagination: PaginationFilter | None,
    ) -> tuple[ExistingResource, ...]:
        """
        Retrieves a list of resources belonging to the ven with the given ven identifier.

        Args:
            ven_id (str): The ven identifier to retrieve.
            resource_name (Optional[str]): The name of the resource to filter on.
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.

        """
        query_params: dict = {}

        if target:
            query_params |= target.model_dump(by_alias=True, mode="json")

        if pagination:
            query_params |= pagination.model_dump(by_alias=True, mode="json")

        if resource_name:
            query_params |= {"resourceName": resource_name}

        logger.debug("Ven - Performing get_ven_resources request with query params: %s", query_params)

        response = self.session.get(f"{self.base_url}/{base_prefix}/{ven_id}/resources", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingResource])
        return tuple(adapter.validate_python(response.json()))

    def get_resource_by_id(self, ven_id: str, resource_id: str) -> ExistingResource:
        """
        Retrieves a resource by the resource identifier belonging to the ven with the given ven identifier.

        Args:
            ven_id (str): The ven identifier to retrieve.
            resource_id (str): The identifier of the resource to retrieve.

        """
        response = self.session.get(f"{self.base_url}/{base_prefix}/{ven_id}/resources/{resource_id}")
        response.raise_for_status()

        return ExistingResource.model_validate(response.json())


class ResourcesWriteOnlyHttpInterface(WriteOnlyResourcesInterface, AuthenticatedHttpInterface):
    """Implements the write communication with the resources HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, config=config, verify_tls_certificate=verify_tls_certificate)

    def update_resource_by_id(self, ven_id: str, resource_id: str, updated_resource: ExistingResource) -> ExistingResource:
        """
        Update the resource with the resource identifier in the VTN.

        If the ven id does not match the ven_id in the existing resource, an error is
        raised.

        If the resource id does not match the id in the existing resource, an error is raised.

        Returns the updated resource response from the VTN.

        Args:
            ven_id (str): The identifier of the ven the resource belongs to.
            resource_id (str): The identifier of the resource to update.
            updated_resource (ExistingResource): The updated resource.

        """
        if ven_id != updated_resource.ven_id:
            exc_msg = "Ven id does not match ven id of updated resource object."
            raise ValueError(exc_msg)

        if resource_id != updated_resource.id:
            exc_msg = "Resource id does not match id of updated resource object."
            raise ValueError(exc_msg)

        # No lock on the ExistingResource type exists similar to the creation guard of a NewResource.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = self.session.put(
            f"{self.base_url}/{base_prefix}/{ven_id}/resources/{resource_id}",
            json=updated_resource.model_dump(by_alias=True, mode="json"),
        )
        response.raise_for_status()
        return ExistingResource.model_validate(response.json())

    def delete_resource_by_id(self, ven_id: str, resource_id: str) -> DeletedResource:
        """
        Delete the resource with the resource identifier in the VTN.

        Args:
            ven_id (str): The identifier of the ven the resource belongs to.
            resource_id (str): The identifier of the resource to delete.

        """
        response = self.session.delete(f"{self.base_url}/{base_prefix}/{ven_id}/resources/{resource_id}")
        response.raise_for_status()

        return DeletedResource.model_validate(response.json())

    def create_resource(self, ven_id: str, new_resource: NewResource) -> ExistingResource:
        """
        Creates a resource from the new resource.

        Returns the created resource response from the VTN as an ExistingResource.

        Args:
            ven_id (str): The identifier of the VEN the resource belongs to.
            new_resource (NewResource): The new resource to create.

        """
        with new_resource.with_creation_guard():
            response = self.session.post(
                f"{self.base_url}/{base_prefix}/{ven_id}/resources",
                json=new_resource.model_dump(by_alias=True, mode="json"),
            )
            response.raise_for_status()
            return ExistingResource.model_validate(response.json())


class ResourcesHttpInterface(ReadWriteResourceInterface, ResourcesReadOnlyHttpInterface, ResourcesWriteOnlyHttpInterface):
    """Implements the read and write communication with the resources HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, config=config, verify_tls_certificate=verify_tls_certificate)
