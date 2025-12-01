"""Implements the abstract base class for the ven VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client._vtn.oadr310.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.oadr310.resource.resource import DeletedResource, ExistingResource, NewResource


class ReadOnlyResourcesInterface(ABC):
    """Abstract class which contains the interface for read only methods of resources."""

    @abstractmethod
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

    @abstractmethod
    def get_resource_by_id(self, ven_id: str, resource_id: str) -> ExistingResource:
        """
        Retrieves a resource by the resource identifier belonging to the ven with the given ven identifier.

        Args:
            ven_id (str): The ven identifier to retrieve.
            resource_id (str): The identifier of the resource to retrieve.

        """


class WriteOnlyResourcesInterface(ABC):
    """Abstract class which contains the interface for write only methods of resources."""

    @abstractmethod
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

    @abstractmethod
    def delete_resource_by_id(self, ven_id: str, resource_id: str) -> DeletedResource:
        """
        Delete the resource with the resource identifier in the VTN.

        Args:
            ven_id (str): The identifier of the ven the resource belongs to.
            resource_id (str): The identifier of the resource to delete.

        """

    @abstractmethod
    def create_resource(self, ven_id: str, new_resource: NewResource) -> ExistingResource:
        """
        Creates a resource from the new resource.

        Returns the created resource response from the VTN as an ExistingResource.

        Args:
            ven_id (str): The identifier of the VEN the resource belongs to.
            new_resource (NewResource): The new resource to create.

        """


class ReadWriteResourceInterface(ReadOnlyResourcesInterface, WriteOnlyResourcesInterface):
    """Class which allows both read and write access on the resource."""
