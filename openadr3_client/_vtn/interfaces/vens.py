"""Implements the abstract base class for the ven VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.ven.resource import ExistingResource, NewResource
from openadr3_client.models.ven.ven import ExistingVen, NewVen


class ReadOnlyVensInterface(ABC):
    """Abstract class which contains the interface for read only methods of vens."""

    @abstractmethod
    def get_vens(
        self, ven_name: str | None, target: TargetFilter | None, pagination: PaginationFilter | None
    ) -> tuple[ExistingVen, ...]:
        """
        Retrieve vens from the VTN.

        Args:
            ven_name (Optional[str]): The ven name to filter on.
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.

        """

    @abstractmethod
    def get_ven_by_id(self, ven_id: str) -> ExistingVen:
        """
        Retrieves a ven by the ven identifier.

        Raises an error if the ven could not be found.

        Args:
            ven_id (str): The ven identifier to retrieve.

        """

    @abstractmethod
    def get_ven_resources(
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
    def get_ven_resource_by_id(self, ven_id: str, resource_id: str) -> ExistingResource:
        """
        Retrieves a resource by the resource identifier belonging to the ven with the given ven identifier.

        Args:
            ven_id (str): The ven identifier to retrieve.
            resource_id (str): The identifier of the resource to retrieve.

        """


class WriteOnlyVensInterface(ABC):
    """Abstract class which contains the interface for write only methods of vens."""

    @abstractmethod
    def create_ven(self, new_ven: NewVen) -> ExistingVen:
        """
        Creates a ven from the new ven.

        Returns the created report response from the VTN as an ExistingReport.

        Args:
            new_ven (NewVen): The new ven to create.

        """

    @abstractmethod
    def update_ven_by_id(self, ven_id: str, updated_ven: ExistingVen) -> ExistingVen:
        """
        Update the ven with the ven identifier in the VTN.

        If the ven id does not match the id in the existing ven, an error is
        raised.

        Returns the updated ven response from the VTN.

        Args:
            ven_id (str): The identifier of the ven to update.
            updated_ven (ExistingVen): The updated ven.

        """

    @abstractmethod
    def delete_ven_by_id(self, ven_id: str) -> None:
        """
        Delete the ven with the identifier in the VTN.

        Args:
            ven_id (str): The identifier of the ven to delete.

        """

    @abstractmethod
    def update_ven_resource_by_id(
        self, ven_id: str, resource_id: str, updated_resource: ExistingResource
    ) -> ExistingResource:
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
    def delete_ven_resource_by_id(self, ven_id: str, resource_id: str) -> None:
        """
        Delete the resource with the resource identifier in the VTN.

        Args:
            ven_id (str): The identifier of the ven the resource belongs to.
            resource_id (str): The identifier of the resource to delete.

        """

    @abstractmethod
    def create_ven_resource(self, ven_id: str, new_resource: NewResource) -> ExistingResource:
        """
        Creates a resource from the new resource.

        Returns the created resource response from the VTN as an ExistingResource.

        Args:
            ven_id (str): The identifier of the VEN the resource belongs to.
            new_resource (NewResource): The new resource to create.

        """


class ReadWriteVensInterface(ReadOnlyVensInterface, WriteOnlyVensInterface):
    """Class which allows both read and write access on the resource."""
