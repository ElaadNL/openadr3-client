"""Implements the communication with the events interface of an OpenADR 3 VTN."""

from dataclasses import asdict

from pydantic.type_adapter import TypeAdapter

from openadr3_client.domain.event.event import ExistingEvent, NewEvent
from openadr3_client.vtn.common._authenticated_session import bearer_authenticated_session
from openadr3_client.vtn.common._vtn_interface import _VtnHttpInterface
from openadr3_client.vtn.common.filters import PaginationFilter, TargetFilter

base_prefix = "events"


class EventsReadOnlyInterface(_VtnHttpInterface):
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
        # Convert the filters to dictionaries and union them. No key clashing can happen, as the properties
        # of the filters are unique.
        query_params = (
            asdict(target)
            if target
            else {} | asdict(pagination)
            if pagination
            else {} | {"programID": program_id}
            if program_id
            else {}
        )

        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingEvent])
        return tuple(adapter.validate_json(response.json()))

    def get_event_by_id(self, event_id: str) -> ExistingEvent:
        """
        Retrieves a event by the event identifier.

        Raises an error if the event could not be found.

        Args:
            event_id (str): The event identifier to retrieve.

        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{event_id}")
        response.raise_for_status()

        return ExistingEvent.model_validate_json(response.json())


class EventsWriteOnlyInterface(_VtnHttpInterface):
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
                f"{self.base_url}/{base_prefix}", data=new_event.model_dump_json()
            )
            response.raise_for_status()
            return ExistingEvent.model_validate_json(response.json())

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
            f"{self.base_url}/{base_prefix}/{event_id}", data=updated_event.model_dump_json()
        )
        response.raise_for_status()
        return ExistingEvent.model_validate_json(response.json())

    def delete_event_by_id(self, event_id: str) -> None:
        """
        Delete the event with the event identifier in the VTN.

        Args:
            event_id (str): The identifier of the event to delete.

        """
        response = bearer_authenticated_session.delete(f"{self.base_url}/{base_prefix}/{event_id}")
        response.raise_for_status()


class EventsInterface(EventsReadOnlyInterface, EventsWriteOnlyInterface):
    """Implements the read and write communication with the events HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
