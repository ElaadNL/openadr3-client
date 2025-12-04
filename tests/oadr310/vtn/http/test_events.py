"""Contains tests for the events VTN module."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic_extra_types.currency_code import ISO4217
from requests import HTTPError

from openadr3_client._vtn.oadr310.http.events import EventsHttpInterface
from openadr3_client._vtn.oadr310.http.programs import ProgramsHttpInterface
from openadr3_client._vtn.oadr310.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.oadr310.common.interval import Interval
from openadr3_client.models.oadr310.common.interval_period import IntervalPeriod
from openadr3_client.models.oadr310.common.target import Target
from openadr3_client.models.oadr310.common.unit import Unit
from openadr3_client.models.oadr310.event.event import EventUpdate, ExistingEvent, NewEvent
from openadr3_client.models.oadr310.event.event_payload import EventPayload, EventPayloadDescriptor, EventPayloadType
from openadr3_client.models.oadr310.program.program import NewProgram
from tests.conftest import IntegrationTestVTNClient

# TODO: Config is None in integration_test_vtn, how to mock it so it works with the bl-token auth? Inheritance?

def test_get_events_non_existent_program_vtn(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events in a VTN with an invalid program returns an empty list."""
    interface = EventsHttpInterface(
        base_url=integration_test_vtn_openadr_310.vtn_base_url,
        config=integration_test_vtn_openadr_310.config,
        verify_tls_certificate=False # Self signed certificate used in integration tests.
    )

    response = interface.get_events(target=None, pagination=None, program_id="fake-program")

    assert len(response) == 0, "no events should be returned by the VTN."


# def test_get_events_no_events_in_vtn(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate that getting events in a VTN without any events returns an empty list."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     response = interface.get_events(target=None, pagination=None, program_id=None)

#     assert len(response) == 0, "no events should be stored in VTN."


# def test_get_event_by_id_non_existent(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate that getting an event by ID in a VTN with no such event raises an exception."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     with pytest.raises(HTTPError, match="404 Client Error"):
#         _ = interface.get_event_by_id(event_id="fake-event-id")


# def test_delete_event_by_id_non_existent(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate that deleting an event by ID in a VTN with no such event raises a 404 error."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     with pytest.raises(HTTPError, match="404 Client Error"):
#         interface.delete_event_by_id(event_id="fake-event-id")


# def test_update_event_by_id_non_existent(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate that updating an event by ID in a VTN with no such event raises a 404 error."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     tz_aware_dt = datetime.now(tz=UTC)
#     with pytest.raises(HTTPError, match="404 Client Error"):
#         interface.update_event_by_id(
#             event_id="fake-event-id",
#             updated_event=ExistingEvent(
#                 id="fake-event-id",
#                 programID="fake-program",
#                 created_date_time=tz_aware_dt,
#                 modification_date_time=tz_aware_dt,
#                 intervals=(
#                     Interval(
#                         id=0,
#                         interval_period=None,
#                         payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
#                     ),
#                 ),
#             ),
#         )


# def test_create_event_invalid_program(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate that creating an event in a VTN with a non existent program fails."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     event = NewEvent(
#         programID="test-program",
#         event_name=None,
#         priority=None,
#         targets=(),
#         payload_descriptors=(),
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

#     with pytest.raises(HTTPError) as e:
#         _ = interface.create_event(new_event=event)

#     assert "A foreign key constraint is violated" in e.value.response.text


# def test_create_event(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate that creating an event in a VTN works correctly."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     program_interface = ProgramsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )
#     program = NewProgram(
#         program_name="test-program",
#         interval_period=IntervalPeriod(
#             start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#             duration=timedelta(minutes=5),
#         ),
#         payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#     )
#     created_program = program_interface.create_program(new_program=program)
#     assert created_program.id is not None, "program should be created successfully"

#     try:
#         # Now create the event
#         event = NewEvent(
#             programID=created_program.id,
#             event_name="test-event",
#             priority=1,
#             targets=(Target(type="test-target", values=("test-value",)),),
#             payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#             interval_period=IntervalPeriod(
#                 start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#                 duration=timedelta(minutes=5),
#             ),
#             intervals=(
#                 Interval(
#                     id=0,
#                     interval_period=None,
#                     payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
#                 ),
#             ),
#         )

#         response = interface.create_event(new_event=event)

#         assert response.id is not None, "event should be created successfully"
#         assert response.program_id == created_program.id, "program id should match"
#         assert response.event_name == "test-event", "event name should match"
#         assert response.priority == 1, "priority should match"
#         assert response.targets is not None and len(response.targets) == 1, "targets should match"
#         assert response.intervals is not None and len(response.intervals) == 1, "intervals should match"

#         interface.delete_event_by_id(event_id=response.id)
#     finally:
#         program_interface.delete_program_by_id(program_id=created_program.id)


# def test_get_events_with_parameters(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate getting events with various parameter combinations."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     # First create a program since events require a program
#     program_interface = ProgramsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )
#     program = NewProgram(
#         program_name="test-program",
#         interval_period=IntervalPeriod(
#             start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#             duration=timedelta(minutes=5),
#         ),
#         payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#     )
#     created_program = program_interface.create_program(new_program=program)
#     assert created_program.id is not None, "program should be created successfully"

#     try:
#         # Create two events with different names and targets
#         event1 = NewEvent(
#             programID=created_program.id,
#             event_name="test-event-1",
#             priority=1,
#             targets=(Target(type="test-target", values=("test-value-1",)),),
#             payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#             interval_period=IntervalPeriod(
#                 start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#                 duration=timedelta(minutes=5),
#             ),
#             intervals=(
#                 Interval(
#                     id=0,
#                     interval_period=None,
#                     payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
#                 ),
#             ),
#         )
#         event2 = NewEvent(
#             programID=created_program.id,
#             event_name="test-event-2",
#             priority=2,
#             targets=(Target(type="test-target", values=("test-value-2",)),),
#             payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#             interval_period=IntervalPeriod(
#                 start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#                 duration=timedelta(minutes=5),
#             ),
#             intervals=(
#                 Interval(
#                     id=0,
#                     interval_period=None,
#                     payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
#                 ),
#             ),
#         )
#         created_event1 = interface.create_event(new_event=event1)
#         created_event2 = interface.create_event(new_event=event2)

#         try:
#             # Test getting all events
#             all_events = interface.get_events(target=None, pagination=None, program_id=None)
#             assert len(all_events) == 2, "Should return both events"

#             # Test getting events by program ID
#             program_events = interface.get_events(target=None, pagination=None, program_id=created_program.id)
#             assert len(program_events) == 2, "Should return both events"

#             # Test getting events by target
#             target_filter = TargetFilter(target_type="test-target", target_values=["test-value-1"])
#             event1_by_target = interface.get_events(target=target_filter, pagination=None, program_id=created_program.id)
#             assert len(event1_by_target) == 1, "Should return one event"
#             assert event1_by_target[0].event_name == "test-event-1", "Should return the correct event"

#             # Test pagination
#             pagination_filter = PaginationFilter(skip=0, limit=1)
#             paginated_events = interface.get_events(target=None, pagination=pagination_filter, program_id=created_program.id)
#             assert len(paginated_events) == 1, "Should return one event due to pagination"
#         finally:
#             interface.delete_event_by_id(event_id=created_event1.id)
#             interface.delete_event_by_id(event_id=created_event2.id)
#     finally:
#         program_interface.delete_program_by_id(program_id=created_program.id)


# def test_delete_event(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate deleting an event that exists."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     # First create a program since events require a program
#     program_interface = ProgramsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )
#     program = NewProgram(
#         program_name="test-program",
#         interval_period=IntervalPeriod(
#             start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#             duration=timedelta(minutes=5),
#         ),
#         payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#     )
#     created_program = program_interface.create_program(new_program=program)
#     assert created_program.id is not None, "program should be created successfully"

#     try:
#         # Create an event to delete
#         event = NewEvent(
#             programID=created_program.id,
#             event_name="test-event-to-delete",
#             priority=1,
#             targets=(Target(type="test-target", values=("test-value",)),),
#             payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#             interval_period=IntervalPeriod(
#                 start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#                 duration=timedelta(minutes=5),
#             ),
#             intervals=(
#                 Interval(
#                     id=0,
#                     interval_period=None,
#                     payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
#                 ),
#             ),
#         )
#         created_event = interface.create_event(new_event=event)
#         assert created_event.id is not None, "event should be created successfully"

#         # Delete the event
#         deleted_event = interface.delete_event_by_id(event_id=created_event.id)

#         assert deleted_event.event_name == "test-event-to-delete", "event name should match"
#         assert deleted_event.priority == 1, "priority should match"
#         assert deleted_event.created_date_time == created_event.created_date_time, "created date time should match"
#         assert deleted_event.modification_date_time == created_event.modification_date_time, "modification date time should match"
#         assert deleted_event.targets is not None, "targets should not be None"
#         assert len(deleted_event.targets) > 0, "targets should not be empty"
#         assert deleted_event.targets[0].values[0] == "test-value", "targets should match"

#         # Verify the event is deleted
#         with pytest.raises(HTTPError, match="404 Client Error"):
#             _ = interface.get_event_by_id(event_id=created_event.id)
#     finally:
#         program_interface.delete_program_by_id(program_id=created_program.id)


# def test_update_event(integration_test_vtn_openadr_310: IntegrationTestVTNClient) -> None:
#     """Test to validate updating an event that exists."""
#     interface = EventsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )

#     # First create a program since events require a program
#     program_interface = ProgramsHttpInterface(
#         base_url=integration_test_vtn_openadr_310.vtn_base_url,
#         config=integration_test_vtn_openadr_310.config,
#     )
#     program = NewProgram(
#         program_name="test-program",
#         interval_period=IntervalPeriod(
#             start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#             duration=timedelta(minutes=5),
#         ),
#         payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#     )
#     created_program = program_interface.create_program(new_program=program)
#     assert created_program.id is not None, "program should be created successfully"

#     try:
#         # Create an event to update
#         event = NewEvent(
#             programID=created_program.id,
#             event_name="test-event-to-update",
#             priority=1,
#             targets=(Target(type="test-target", values=("test-value",)),),
#             payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
#             interval_period=IntervalPeriod(
#                 start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
#                 duration=timedelta(minutes=5),
#             ),
#             intervals=(
#                 Interval(
#                     id=0,
#                     interval_period=None,
#                     payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
#                 ),
#             ),
#         )
#         created_event = interface.create_event(new_event=event)
#         assert created_event.id is not None, "event should be created successfully"

#         try:
#             # Update the event
#             event_update = EventUpdate(
#                 event_name="test-event-updated",
#                 priority=2,
#                 targets=(Target(type="test-target", values=("test-value-updated",)),),
#             )

#             updated_event = interface.update_event_by_id(event_id=created_event.id, updated_event=created_event.update(event_update))

#             # Verify the update
#             assert updated_event.event_name == "test-event-updated", "event name should be updated"
#             assert updated_event.priority == 2, "priority should be updated"
#             assert updated_event.created_date_time == created_event.created_date_time, "created date time should match"
#             assert updated_event.modification_date_time != created_event.modification_date_time, "modification date time should not match"
#             assert updated_event.targets is not None, "targets should not be None"
#             assert len(updated_event.targets) > 0, "targets should not be empty"
#             assert updated_event.targets[0].values[0] == "test-value-updated", "target values should be updated"
#         finally:
#             interface.delete_event_by_id(event_id=created_event.id)
#     finally:
#         program_interface.delete_program_by_id(program_id=created_program.id)
