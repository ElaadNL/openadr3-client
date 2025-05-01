"""Implements the communication with the events interface of an OpenADR 3 VTN."""
from typing import List, Tuple

from pydantic.type_adapter import TypeAdapter
from openadr3_client.vtn.common.filters import PaginationFilter, TargetFilter
from openadr3_client.domain.event.event import ExistingEvent, NewEvent
from openadr3_client.vtn.common._authenticated_session import bearer_authenticated_session

from dataclasses import asdict

base_prefix = "/events"

def get_events(self, target: TargetFilter, pagination: PaginationFilter) -> Tuple[ExistingEvent, ...]:
    """Retrieve events from the VTN.
    
    Args:
        target (TargetFilter): The target to filter on.
        pagination (PaginationFilter): The pagination to apply.
    """

    # Convert the filters to dictionaries and union them. No key clashing can happen, as the properties
    # of the filters are unique.
    query_params = asdict(target) | asdict(pagination)

    response = bearer_authenticated_session.get(f"{base_prefix}", params=query_params)
    response.raise_for_status()

    adapter = TypeAdapter(List[ExistingEvent])
    return tuple(adapter.validate_json(response.json()))

def get_event_by_id(self, event_id: str) -> ExistingEvent:
    """Retrieves a event by the event identifier.
    
    Raises an error if the program could not be found.
    
    Args:
        event_id (str): The event identifier to retrieve.
    """
    response = bearer_authenticated_session.get(f"{base_prefix}/{event_id}")
    response.raise_for_status()

    return ExistingEvent.model_validate_json(response.json())

def create_event(self, new_event: NewEvent) -> ExistingEvent:
    """Creates a event from the new event.
    
    Returns the created event response from the VTN as an ExistingEvent.
    
    Args:
        new_event (NewEvent): The new event to create.
    """
    with new_event.with_creation_guard():
        response = bearer_authenticated_session.post(base_prefix, data=new_event.model_dump_json())
        response.raise_for_status()
        return ExistingEvent.model_validate_json(response.json())

def update_event_by_id(self, event_id: str, updated_event: ExistingEvent) -> ExistingEvent:
    """Update the event with the event identifier in the VTN.

    If the event id does not match the id in the existing event, an error is
    raised.

    Returns the updated event response from the VTN.

    Args:
        event_id (str): The identifier of the event to update.
        updated_event (ExistingProgram): The updated event.
    """
    if event_id != updated_event.id:
        raise ValueError("Event id does not match event id of updated event object.")
    
    # No lock on the ExistingEvent type exists similar to the creation guard of a NewEvent.
    # Since calling update with the same object multiple times is an idempotent action that does not
    # result in a state change in the VTN.
    response = bearer_authenticated_session.put(f"{base_prefix}/{event_id}",
                                                data=updated_event.model_dump_json())
    response.raise_for_status()
    return ExistingEvent.model_validate_json(response.json())

def delete_event_by_id(self, event_id: str) -> None:
    """Delete the event with the event identifier in the VTN.

    Args:
        event_id (str): The identifier of the event to delete.
    """
    response = bearer_authenticated_session.delete(f"{base_prefix}/{event_id}")
    response.raise_for_status()