"""Implements the abstract base classes for VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.event.event import ExistingEvent, NewEvent


class ReadOnlyEventsInterface(ABC):
    """Abstract class which contains the interface for read only methods of events."""

    @abstractmethod
    def get_events(
        self, target: TargetFilter | None, pagination: PaginationFilter | None, program_id: str | None
    ) -> tuple[ExistingEvent, ...]:
        """
        Retrieve events from the VTN.

        Args:
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.
            program_id (Optional[str]): The program id to filter on.

        """

    @abstractmethod
    def get_event_by_id(self, event_id: str) -> ExistingEvent:
        """
        Retrieves a event by the event identifier.

        Raises an error if the event could not be found.

        Args:
            event_id (str): The event identifier to retrieve.

        """


class WriteOnlyEventsInterface(ABC):
    """Abstract class which contains the interface for write only methods of events."""

    @abstractmethod
    def create_event(self, new_event: NewEvent) -> ExistingEvent:
        """
        Creates a event from the new event.

        Returns the created event response from the VTN as an ExistingEvent.

        Args:
            new_event (NewEvent): The new event to create.

        """

    @abstractmethod
    def update_event_by_id(self, event_id: str, updated_event: ExistingEvent) -> ExistingEvent:
        """
        Update the event with the event identifier in the VTN.

        If the event id does not match the id in the existing event, an error is
        raised.

        Returns the updated event response from the VTN.

        Args:
            event_id (str): The identifier of the event to update.
            updated_event (ExistingEvent): The updated event.

        """

    @abstractmethod
    def delete_event_by_id(self, event_id: str) -> None:
        """
        Delete the event with the event identifier in the VTN.

        Args:
            event_id (str): The identifier of the event to delete.

        """


class ReadWriteEventsInterface(ReadOnlyEventsInterface, WriteOnlyEventsInterface):
    """Class which allows both read and write access on the events resource."""
