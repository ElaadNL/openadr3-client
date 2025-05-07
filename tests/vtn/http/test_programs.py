"""Contains tests for the programs VTN module."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic_extra_types.currency_code import ISO4217
from requests.exceptions import HTTPError

from openadr3_client._vtn.http.programs import ProgramsHttpInterface
from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.common.target import Target
from openadr3_client.models.common.unit import Unit
from openadr3_client.models.event.event_payload import EventPayloadDescriptor, EventPayloadType
from openadr3_client.models.program.program import ExistingProgram, NewProgram, ProgramUpdate
from tests.conftest import IntegrationTestVTNClient


def test_get_programs_no_programs_in_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting programs in a VTN without any programs returns an empty list."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    response = interface.get_programs(target=None, pagination=None)

    assert len(response) == 0, "no programs should be stored in VTN."


def test_get_program_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a program by ID in a VTN with no such program raises an exception."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_program_by_id(program_id="fake-program-id")


def test_delete_program_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a program by ID in a VTN with no such program raises a 404 error."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_program_by_id(program_id="fake-program-id")


def test_update_program_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a program by ID in a VTN with no such program raises a 404 error."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    tz_aware_dt = datetime.now(tz=UTC)
    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.update_program_by_id(
            program_id="fake-program-id",
            updated_program=ExistingProgram(
                id="fake-program-id",
                program_name="Test Program",
                created_date_time=tz_aware_dt,
                modification_date_time=tz_aware_dt,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                ),
                payload_descriptor=(
                    EventPayloadDescriptor(
                        payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")
                    ),
                ),
            ),
        )


def test_create_program(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a program in a VTN works correctly."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    program = NewProgram(
        program_name="Test Program",
        program_long_name="Test Program Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
            randomize_start=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
    )

    response = interface.create_program(new_program=program)

    assert response.id is not None, "program should be created successfully."
    assert response.program_name == "Test Program", "program name should match"
    assert response.program_long_name == "Test Program Long Name", "program long name should match"

    interface.delete_program_by_id(program_id=response.id)


def test_get_programs_with_parameters(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate getting programs with various parameter combinations."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # Create two programs with different names and targets
    program1 = NewProgram(
        program_name="test-program-1",
        program_long_name="Test Program 1 Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
        targets=(Target(type="test-target-1", values=("test-value-1",)),),
    )
    program2 = NewProgram(
        program_name="test-program-2",
        program_long_name="Test Program 2 Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
        targets=(Target(type="test-target-2", values=("test-value-2",)),),
    )
    created_program1 = interface.create_program(new_program=program1)
    created_program2 = interface.create_program(new_program=program2)

    try:
        # Test getting all programs
        all_programs = interface.get_programs(target=None, pagination=None)
        assert len(all_programs) == 2, "Should return both programs"

        # Test getting programs by target
        target_filter = TargetFilter(target_type="test-target-1", target_values=["test-value-1"])
        program1_by_target = interface.get_programs(target=target_filter, pagination=None)
        assert len(program1_by_target) == 1, "Should return one program"
        assert program1_by_target[0].program_name == "test-program-1", "Should return the correct program"

        # Test pagination
        pagination_filter = PaginationFilter(skip=0, limit=1)
        paginated_programs = interface.get_programs(target=None, pagination=pagination_filter)
        assert len(paginated_programs) == 1, "Should return one program due to pagination"
    finally:
        interface.delete_program_by_id(program_id=created_program1.id)
        interface.delete_program_by_id(program_id=created_program2.id)


def test_delete_program(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate deleting a program that exists."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # Create a program to delete
    program = NewProgram(
        program_name="test-program-to-delete",
        program_long_name="Test Program To Delete Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_program = interface.create_program(new_program=program)
    assert created_program.id is not None, "program should be created successfully"

    # Delete the program
    interface.delete_program_by_id(program_id=created_program.id)

    # Verify the program is deleted
    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_program_by_id(program_id=created_program.id)


def test_update_program(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate updating a program that exists."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # Create a program to update
    program = NewProgram(
        program_name="test-program-to-update",
        program_long_name="Test Program To Update Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
        targets=(Target(type="test-target", values=("test-value",)),),
    )
    created_program = interface.create_program(new_program=program)
    assert created_program.id is not None, "program should be created successfully"

    try:
        # Update the program
        program_update = ProgramUpdate(
            program_name="test-program-updated",
            program_long_name="Test Program Updated Long Name",
            interval_period=IntervalPeriod(
                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                duration=timedelta(minutes=5),
            ),
            payload_descriptor=(
                EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
            ),
            targets=(Target(type="test-target-updated", values=("test-value-updated",)),),
        )

        updated_program = interface.update_program_by_id(
            program_id=created_program.id, updated_program=created_program.update(program_update)
        )

        # Verify the update
        assert updated_program.program_name == "test-program-updated", "program name should be updated"
        assert updated_program.program_long_name == "Test Program Updated Long Name", (
            "program long name should be updated"
        )
        assert updated_program.created_date_time == created_program.created_date_time, "created date time should match"
        assert updated_program.modification_date_time != created_program.modification_date_time, (
            "modification date time should not match"
        )
        assert updated_program.targets is not None, "targets should not be None"
        assert len(updated_program.targets) > 0, "targets should not be empty"
        assert updated_program.targets[0].type == "test-target-updated", "target type should be updated"
        assert updated_program.targets[0].values == ("test-value-updated",), "target values should be updated"
    finally:
        interface.delete_program_by_id(program_id=created_program.id)
