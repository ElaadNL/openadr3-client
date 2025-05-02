"""Implements the communication with the events interface of an OpenADR 3 VTN."""

from typing import final

from pydantic.type_adapter import TypeAdapter

from openadr3_client._vtn.http.common._authenticated_session import bearer_authenticated_session
from openadr3_client._vtn.http.http_interface import HttpInterface
from openadr3_client._vtn.interfaces.events import (
    ReadOnlyEventsInterface,
    ReadWriteEventsInterface,
    WriteOnlyEventsInterface,
)
from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.logging import logger
from openadr3_client.models.event.event import ExistingEvent, NewEvent

base_prefix = "events"


class EventsReadOnlyHttpInterface(ReadOnlyEventsInterface, HttpInterface):
    """Implements the read communication with the events HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

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
        query_params: dict = {}

        if target:
            query_params |= target.model_dump(by_alias=True, mode="json")

        if pagination:
            query_params |= pagination.model_dump(by_alias=True, mode="json")

        if program_id:
            query_params |= {"programID": program_id}

        logger.debug("Events - Performing get_events request with query params: %s", query_params)

        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingEvent])
        return tuple(adapter.validate_python(response.json()))

    def get_event_by_id(self, event_id: str) -> ExistingEvent:
        """
        Retrieves a event by the event identifier.

        Raises an error if the event could not be found.

        Args:
            event_id (str): The event identifier to retrieve.

        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{event_id}")
        response.raise_for_status()

        return ExistingEvent.model_validate(response.json())


class EventsWriteOnlyHttpInterface(WriteOnlyEventsInterface, HttpInterface):
    """Implements the write communication with the events HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def create_event(self, new_event: NewEvent) -> ExistingEvent:
        """
        Creates a event from the new event.

        Returns the created event response from the VTN as an ExistingEvent.

        Args:
            new_event (NewEvent): The new event to create.

        """
        with new_event.with_creation_guard():
            response = bearer_authenticated_session.post(
                f"{self.base_url}/{base_prefix}", json=new_event.model_dump(by_alias=True, mode="json")
            )
            response.raise_for_status()
            return ExistingEvent.model_validate(response.json())

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
        if event_id != updated_event.id:
            exc_msg = "Event id does not match event id of updated event object."
            raise ValueError(exc_msg)

        # No lock on the ExistingEvent type exists similar to the creation guard of a NewEvent.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(
            f"{self.base_url}/{base_prefix}/{event_id}", json=updated_event.model_dump(by_alias=True, mode="json")
        )
        response.raise_for_status()
        return ExistingEvent.model_validate(response.json())

    def delete_event_by_id(self, event_id: str) -> None:
        """
        Delete the event with the event identifier in the VTN.

        Args:
            event_id (str): The identifier of the event to delete.

        """
        response = bearer_authenticated_session.delete(f"{self.base_url}/{base_prefix}/{event_id}")
        response.raise_for_status()


@final
class EventsHttpInterface(ReadWriteEventsInterface, EventsReadOnlyHttpInterface, EventsWriteOnlyHttpInterface):
    """Implements the read and write communication with the events HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
