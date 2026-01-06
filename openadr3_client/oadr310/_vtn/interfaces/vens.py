"""Implements the abstract base class for the ven VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client.oadr310._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.oadr310.models.ven.ven import DeletedVen, ExistingVen, NewVenVenRequest, VenUpdate


class ReadOnlyVensInterface(ABC):
    """Abstract class which contains the interface for read only methods of vens."""

    @abstractmethod
    def get_vens(self, ven_name: str | None, target: TargetFilter | None, pagination: PaginationFilter | None) -> tuple[ExistingVen, ...]:
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


class WriteOnlyVensInterface(ABC):
    """Abstract class which contains the interface for write only methods of vens."""

    @abstractmethod
    def create_ven(self, new_ven: NewVenVenRequest) -> ExistingVen:
        """
        Creates a ven from the new ven.

        Returns the created report response from the VTN as an ExistingReport.

        Args:
            new_ven (NewVen): The new ven to create.

        """

    @abstractmethod
    def update_ven_by_id(self, ven_id: str, updated_ven: VenUpdate) -> ExistingVen:
        """
        Update the ven with the ven identifier in the VTN.

        If the ven id does not match the id in the existing ven, an error is
        raised.

        Returns the updated ven response from the VTN.

        Args:
            ven_id (str): The identifier of the ven to update.
            updated_ven (ExistingVen): The ven update to apply.

        """

    @abstractmethod
    def delete_ven_by_id(self, ven_id: str) -> DeletedVen:
        """
        Delete the ven with the identifier in the VTN.

        Returns the deleted ven response from the VTN.

        Args:
            ven_id (str): The identifier of the ven to delete.

        """


class ReadWriteVensInterface(ReadOnlyVensInterface, WriteOnlyVensInterface):
    """Class which allows both read and write access on the resource."""
