"""Implements the abstract base class for the ven VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client.oadr310._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.oadr310.models.resource.resource import DeletedResource, ExistingResource, NewResource, ResourceUpdate


class ReadOnlyResourcesInterface(ABC):
    """Abstract class which contains the interface for read only methods of resources."""

    @abstractmethod
    def get_resources(
        self,
        ven_id: str | None = None,
        resource_name: str | None = None,
        target: TargetFilter | None = None,
        pagination: PaginationFilter | None = None,
    ) -> tuple[ExistingResource, ...]:
        """
        Retrieves a list of resources belonging to the ven with the given ven identifier.

        Args:
            ven_id: The ven identifier to retrieve.
            resource_name: The name of the resource to filter on.
            target: The target to filter on.
            pagination: The pagination to apply.

        """

    @abstractmethod
    def get_resource_by_id(self, resource_id: str) -> ExistingResource:
        """
        Retrieves a resource by the resource identifier belonging to the ven with the given ven identifier.

        Args:
            resource_id: The identifier of the resource to retrieve.

        """


class WriteOnlyResourcesInterface(ABC):
    """Abstract class which contains the interface for write only methods of resources."""

    @abstractmethod
    def update_resource_by_id(self, resource_id: str, updated_resource: ResourceUpdate) -> ExistingResource:
        """
        Update the resource with the resource identifier in the VTN.

        If the ven id does not match the ven_id in the existing resource, an error is
        raised.

        If the resource id does not match the id in the existing resource, an error is raised.

        Returns the updated resource response from the VTN.

        Args:
            resource_id: The identifier of the resource to update.
            updated_resource: The resource update to apply.

        """

    @abstractmethod
    def delete_resource_by_id(self, resource_id: str) -> DeletedResource:
        """
        Delete the resource with the resource identifier in the VTN.

        Args:
            resource_id: The identifier of the resource to delete.

        """

    @abstractmethod
    def create_resource(self, new_resource: NewResource) -> ExistingResource:
        """
        Creates a resource from the new resource.

        Returns the created resource response from the VTN as an ExistingResource.

        Args:
            new_resource: The new resource to create.

        """


class ReadWriteResourceInterface(ReadOnlyResourcesInterface, WriteOnlyResourcesInterface):
    """Class which allows both read and write access on the resource."""
