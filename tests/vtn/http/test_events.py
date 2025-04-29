"""Contains tests for the events VTN module."""

import pytest
from requests import HTTPError
from openadr3_client._vtn.http.events import EventsHttpInterface
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.event.event import ExistingEvent, NewEvent
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadType
from tests.conftest import IntegrationTestVTNClient

from datetime import UTC, datetime, timedelta, timezone


def test_get_events_non_existent_program_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events in a VTN with an invalid program returns an empty list."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    
    response = interface.get_events(target=None, pagination=None, program_id="fake-program")

    assert len(response) == 0, "no events should be returned by the VTN." 

def test_get_events_no_events_in_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events in a VTN without any events returns an empty list."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    response = interface.get_events(target=None, pagination=None, program_id=None)

    assert len(response) == 0, "no events should be stored in VTN."

def test_get_event_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting an event by ID in a VTN with no such event raises an exception."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_event_by_id(event_id="fake-event-id")
        
def test_delete_event_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting an event by ID in a VTN with no such event raises a 404 error."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_event_by_id(event_id="fake-event-id")

def test_update_event_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating an event by ID in a VTN with no such event raises a 404 error."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    
    with pytest.raises(HTTPError, match="404 Client Error"):
        tz_aware_dt = datetime.now(tz=timezone.utc)
        interface.update_event_by_id(
            event_id="fake-event-id",
            updated_event=ExistingEvent(id="fake-event-id",
                                        programID="fake-program",
                                        created_date_time=tz_aware_dt,
                                        modification_date_time=tz_aware_dt,
                                        intervals=(
                                            Interval(
                                                id=0,
                                                interval_period=None,
                                                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),)
                                            ),
                                        )))
        
def test_create_event_invalid_program(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating an event in a VTN with a non existent program fails."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    event = NewEvent(
        id=None,
        programID="test-program",
        event_name=None,
        priority=None,
        targets=(),
        payload_descriptor=(),
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        intervals=(
            Interval(
                id=0,
                interval_period=None,
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        ),
    )

    with pytest.raises(HTTPError) as e:
        _ = interface.create_event(new_event=event)
        
    assert "A foreign key constraint is violated" in e.value.response.text

# def test_create_event_valid_program_id(integration_test_vtn_client: IntegrationTestVTNClient):
#     interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

#     event = NewEvent(
#         id=None,
#         programID="test-program",
#         event_name=None,
#         priority=None,
#         targets=(),
#         payload_descriptor=(),
#         interval_period=IntervalPeriod(
#             start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#             duration=timedelta(minutes=5),
#         ),
#         intervals=(
#             Interval(
#                 id=0,
#                 interval_period=None,
#                 payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
#             ),
#         ),
#     )

#     response = interface.create_event(new_event=event)

#     assert response.id is not None, "event should be created successfully."
    