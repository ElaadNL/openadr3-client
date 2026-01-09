"""Contains tests for the events VTN module."""

from datetime import UTC, datetime, timedelta

import pytest
from requests import HTTPError

from openadr3_client._models.common.interval import Interval
from openadr3_client._models.common.interval_period import IntervalPeriod
from openadr3_client.oadr310._vtn.http.events import EventsHttpInterface
from openadr3_client.oadr310._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.oadr310.models.event.event import EventUpdate, NewEvent
from openadr3_client.oadr310.models.event.event_payload import EventPayload, EventPayloadType
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import event_in_program_with_targets, new_program, resource_for_ven, ven_with_targets


def test_get_events_non_existent_program_vtn(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events in a VTN with an invalid program returns an empty list."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    response = interface.get_events(target=None, pagination=None, program_id="fake-program")

    assert len(response) == 0, "no events should be returned by the VTN."


def test_get_events_no_events_in_vtn(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events in a VTN without any events returns an empty list."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    response = interface.get_events(target=None, pagination=None, program_id=None)

    assert len(response) == 0, "no events should be stored in VTN."


def test_get_event_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting an event by ID in a VTN with no such event raises an exception."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_event_by_id(event_id="fake-event-id")


def test_delete_event_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting an event by ID in a VTN with no such event raises a 404 error."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_event_by_id(event_id="fake-event-id")


def test_update_event_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that updating an event by ID in a VTN with no such event raises a 404 error."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.update_event_by_id(
            event_id="fake-event-id",
            updated_event=EventUpdate(
                programID="fake-program",
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                intervals=(
                    Interval(
                        id=0,
                        interval_period=IntervalPeriod(
                            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                            duration=timedelta(minutes=5),
                            randomize_start=timedelta(seconds=0),
                        ),
                        payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
                    ),
                ),
                duration=timedelta(seconds=1),
            ),
        )


def test_create_event_invalid_program(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that creating an event in a VTN with a non existent program fails."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    event = NewEvent(
        programID="test-program",
        event_name=None,
        priority=None,
        targets=(),
        payload_descriptors=(),
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
            randomize_start=timedelta(seconds=0),
        ),
        intervals=(
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        ),
        duration=timedelta(seconds=0),
    )

    with pytest.raises(HTTPError) as e:
        _ = interface.create_event(new_event=event)

    assert "program_id does not refer to an existing program" in e.value.response.text


def test_create_event(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that creating an event in a VTN works correctly."""
    with new_program(vtn_openadr_310_bl_token, program_name="test-program") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        intervals = (
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        )

        with event_in_program_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            program=created_program,
            intervals=intervals,
            event_name="test-event",
        ) as created_event:
            assert created_event.id is not None, "event should be created successfully"
            assert created_event.program_id == created_program.id, "program id should match"
            assert created_event.event_name == "test-event", "event name should match"
            assert created_event.priority is None, "priority should match"
            assert created_event.targets is not None and len(created_event.targets) == 0, "targets should be empty"
            assert created_event.intervals == intervals, "intervals should match"


def test_get_events_with_parameters(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate getting events with various parameter combinations."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with new_program(vtn_openadr_310_bl_token, program_name="test-program2") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        intervals = (
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        )

        with (
            event_in_program_with_targets(
                vtn_client=vtn_openadr_310_bl_token,
                program=created_program,
                intervals=intervals,
                event_name="test-event-1",
                targets=("test-value-1",),
            ) as event1,
            event_in_program_with_targets(
                vtn_client=vtn_openadr_310_bl_token,
                program=created_program,
                intervals=intervals,
                event_name="test-event-2",
                targets=("test-value-2",),
            ),
        ):
            # Test getting all events
            all_events = interface.get_events(target=None, pagination=None, program_id=None)
            assert len(all_events) == 2, "Should return both events"

            # Test getting events by program ID
            program_events = interface.get_events(target=None, pagination=None, program_id=created_program.id)
            assert len(program_events) == 2, "Should return both events"

            # Test getting events by target
            target_filter = TargetFilter(targets=["test-value-1"])
            event1_by_target = interface.get_events(target=target_filter, pagination=None, program_id=created_program.id)
            assert len(event1_by_target) == 1, "Should return one event"
            assert event1_by_target[0] == event1, "Should return the correct event"

            # Test pagination
            pagination_filter = PaginationFilter(skip=0, limit=1)
            paginated_events = interface.get_events(target=None, pagination=pagination_filter, program_id=created_program.id)
            assert len(paginated_events) == 1, "Should return one event due to pagination"


def test_delete_event(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate deleting an event that exists."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with new_program(vtn_openadr_310_bl_token, program_name="test-program3") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        intervals = (
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        )

        with event_in_program_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            program=created_program,
            intervals=intervals,
            event_name="test-event-to-delete",
            targets=("test-value",),
        ) as created_event:
            assert created_event.id is not None, "event should be created successfully"

            # Delete the event
            deleted_event = interface.delete_event_by_id(event_id=created_event.id)

            assert deleted_event.event_name == "test-event-to-delete", "event name should match"
            assert deleted_event.priority is None, "priority should match"
            assert deleted_event.created_date_time == created_event.created_date_time, "created date time should match"
            assert deleted_event.modification_date_time == created_event.modification_date_time, "modification date time should match"
            assert deleted_event.targets is not None, "targets should not be None"
            assert len(deleted_event.targets) > 0, "targets should not be empty"
            assert deleted_event.targets[0] == "test-value", "targets should match"

        # Verify the event is deleted
        with pytest.raises(HTTPError, match="404 Client Error"):
            _ = interface.get_event_by_id(event_id=created_event.id)


def test_update_event(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate updating an event that exists."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with new_program(vtn_openadr_310_bl_token, program_name="test-program4") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        intervals = (
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        )

        with event_in_program_with_targets(
            vtn_client=vtn_openadr_310_bl_token,
            program=created_program,
            intervals=intervals,
            event_name="test-event-to-update",
            targets=("test-value",),
        ) as created_event:
            assert created_event.id is not None, "event should be created successfully"

            # Update the event
            event_update = EventUpdate(
                programID=created_program.id,
                event_name="test-event-updated",
                priority=2,
                targets=("test-value-updated",),
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                intervals=(),
                duration=timedelta(seconds=0),
            )

            updated_event = interface.update_event_by_id(event_id=created_event.id, updated_event=event_update)

            # Verify the update
            assert updated_event.event_name == "test-event-updated", "event name should be updated"
            assert updated_event.priority == 2, "priority should be updated"
            assert updated_event.created_date_time == created_event.created_date_time, "created date time should match"
            assert updated_event.targets is not None, "targets should not be None"
            assert len(updated_event.targets) > 0, "targets should not be empty"
            assert updated_event.targets[0] == "test-value-updated", "target values should be updated"


def test_ven_get_events_no_events(vtn_openadr_310_ven_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events in a VTN without any events returns an empty list for a VEN token."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    response = interface.get_events(target=None, pagination=None, program_id=None)

    assert len(response) == 0, "no events should be stored in VTN."


def test_ven_get_targeted_events(vtn_openadr_310_ven_token: IntegrationTestVTNClient, vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """
    Test to validate that VENs are able to see targeted events.

    Validates that events with targets that are in the allowed targets list of the ven object of that client
    are visible to that VEN.
    """
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with new_program(vtn_openadr_310_bl_token, program_name="test-program5") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        targets = ("ven-target",)

        with ven_with_targets(vtn_openadr_310_bl_token, ven_name="targeted-ven", client_id_of_ven=vtn_openadr_310_ven_token.config.client_id, targets=targets):
            event_name = "targeted-event"
            intervals = (
                Interval(
                    id=0,
                    interval_period=IntervalPeriod(
                        start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                        duration=timedelta(minutes=5),
                        randomize_start=timedelta(seconds=0),
                    ),
                    payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
                ),
            )

            with (
                event_in_program_with_targets(
                    vtn_client=vtn_openadr_310_bl_token,
                    program=created_program,
                    intervals=intervals,
                    targets=targets,
                    event_name=event_name,
                ),
                event_in_program_with_targets(
                    vtn_client=vtn_openadr_310_bl_token,
                    program=created_program,
                    intervals=intervals,
                    targets=("other-target",),
                    event_name="not-targeted-event",
                ),
            ):
                response = interface.get_events(target=None, pagination=None, program_id=None)
                assert len(response) == 1, "one event should be returned by the VTN."
                assert response[0].event_name == event_name, "the event should have the correct name."

                response = interface.get_events(target=TargetFilter(targets=list(targets)), pagination=None, program_id=None)
                assert len(response) == 1, "one event should be returned by the VTN."
                assert response[0].event_name == event_name, "the event should have the correct name."


def test_ven_with_resource_target_gets_targeted_events(vtn_openadr_310_ven_token: IntegrationTestVTNClient, vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Validate that a VEN with an associated resource with targets can see events with those targets."""
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with new_program(vtn_openadr_310_bl_token, program_name="test-program-resource-target") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        resource_targets = ("resource-target",)
        intervals = (
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(seconds=0),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        )

        with (
            ven_with_targets(
                vtn_openadr_310_bl_token,
                ven_name="ven-with-resource-target",
                client_id_of_ven=vtn_openadr_310_ven_token.config.client_id,
            ) as ven,
            resource_for_ven(
                vtn_client=vtn_openadr_310_bl_token,
                ven_id=ven.id,
                resource_name="resource-targeted",
                client_id_of_resource=ven.client_id,
                attributes=None,
                targets=resource_targets,
            ),
            event_in_program_with_targets(
                vtn_client=vtn_openadr_310_bl_token,
                program=created_program,
                intervals=intervals,
                targets=resource_targets,
                event_name="resource-targeted-event",
            ) as targeted_event,
            event_in_program_with_targets(
                vtn_client=vtn_openadr_310_bl_token,
                program=created_program,
                intervals=intervals,
                targets=("other-target",),
                event_name="not-targeted-event",
            ),
        ):
            response = interface.get_events(target=None, pagination=None, program_id=None)
            assert len(response) == 1, "one event should be returned by the VTN."
            assert response[0].event_name == targeted_event.event_name, "the event should have the correct name."

            response = interface.get_events(target=TargetFilter(targets=list(resource_targets)), pagination=None, program_id=None)
            assert len(response) == 1, "one event should be returned by the VTN."
            assert response[0].event_name == targeted_event.event_name, "the event should have the correct name."


def test_ven_should_not_see_other_targeted_events(vtn_openadr_310_ven_token: IntegrationTestVTNClient, vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """
    Test to validate that events can only be seen by the appropriate VEN.

    Validates that events with targets that are not in the allowed targets list of the ven object of that client
    are not visible to that VEN. Even if they target them manually.
    """
    interface = EventsHttpInterface(
        base_url=vtn_openadr_310_ven_token.vtn_base_url,
        config=vtn_openadr_310_ven_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with new_program(vtn_openadr_310_bl_token, program_name="test-program6") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        targets = ("ven-target",)

        with ven_with_targets(vtn_openadr_310_bl_token, ven_name="not-targeted-ven", client_id_of_ven=vtn_openadr_310_ven_token.config.client_id, targets=targets):
            intervals = (
                Interval(
                    id=0,
                    interval_period=IntervalPeriod(
                        start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                        duration=timedelta(minutes=5),
                        randomize_start=timedelta(seconds=0),
                    ),
                    payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
                ),
            )

            with event_in_program_with_targets(
                vtn_client=vtn_openadr_310_bl_token,
                program=created_program,
                intervals=intervals,
                targets=("other-target",),
                event_name="not-targeted-event",
            ):
                response = interface.get_events(target=None, pagination=None, program_id=None)
                assert len(response) == 0, "No events should be seen the VEN."

                # Even knowing the target, the VEN should not be able to find the event even if filtering on it.
                response = interface.get_events(target=TargetFilter(targets=list(targets)), pagination=None, program_id=None)
                assert len(response) == 0, "No events should be seen the VEN."
