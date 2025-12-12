"""Contains tests for the programs VTN module."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic_extra_types.currency_code import ISO4217
from requests.exceptions import HTTPError

from openadr3_client.oadr310._vtn.http.programs import ProgramsHttpInterface
from openadr3_client.oadr310._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.oadr310.models.common.interval_period import IntervalPeriod
from openadr3_client.oadr310.models.common.unit import Unit
from openadr3_client.oadr310.models.event.event_payload import EventPayloadDescriptor, EventPayloadType
from openadr3_client.oadr310.models.program.program import ExistingProgram, ProgramUpdate
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import new_program


def test_get_programs_no_programs_in_vtn(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting programs in a VTN without any programs returns an empty list."""
    interface = ProgramsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    response = interface.get_programs(target=None, pagination=None)

    assert len(response) == 0, "no programs should be stored in VTN."


def test_get_program_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a program by ID in a VTN with no such program raises an exception."""
    interface = ProgramsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_program_by_id(program_id="fake-program-id")


def test_delete_program_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a program by ID in a VTN with no such program raises a 404 error."""
    interface = ProgramsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_program_by_id(program_id="fake-program-id")


def test_update_program_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a program by ID in a VTN with no such program raises a 404 error."""
    interface = ProgramsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    tz_aware_dt = datetime.now(tz=UTC)
    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.update_program_by_id(
            program_id="fake-program-id",
            updated_program=ExistingProgram(
                id="fake-program-id",
                program_name="Test Program",
                created_date_time=tz_aware_dt,
                modification_date_time=tz_aware_dt,
                interval_period=IntervalPeriod(start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC), duration=timedelta(minutes=5), randomize_start=timedelta(seconds=0)),
                payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
            ),
        )


def test_create_program(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a program in a VTN works correctly."""
    targets_of_program = (
        "test-target-1",
        "test-target-2",
    )
    with new_program(vtn_client=vtn_openadr_310_bl_token, program_name="test-program", targets=targets_of_program) as program:
        assert program.id is not None, "program should be created successfully."
        assert program.program_name == "test-program", "program name should match"
        assert program.program_long_name is None, "program long name should match"
        assert program.retailer_name is None, "retailer name should match"
        assert program.retailer_long_name is None, "retailer long name should match"
        assert program.program_type is None, "program type should match"
        assert program.country is None, "country should match"
        assert program.principal_subdivision is None, "principal subdivision should match"
        assert program.program_descriptions is None, "program descriptions should match"
        assert program.binding_events is None, "binding events should match"
        assert program.local_price is None, "local price should match"
        assert program.targets == targets_of_program, "targets should be empty"


def test_get_programs_with_parameters(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate getting programs with various parameter combinations."""
    interface = ProgramsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    targets_of_program1 = ("test-target-1",)
    targets_of_program2 = ("test-target-2",)

    # Create two programs with different names and targets
    with (
        new_program(vtn_client=vtn_openadr_310_bl_token, program_name="test-program-1", targets=targets_of_program1) as program1,
        new_program(vtn_client=vtn_openadr_310_bl_token, program_name="test-program-2", targets=targets_of_program2) as program2,
    ):
        # Test getting all programs
        all_programs = interface.get_programs(target=None, pagination=None)
        assert len(all_programs) == 2, "Should return both programs"

        # Test getting programs by target
        target_filter = TargetFilter(targets=list(targets_of_program1))
        program1_by_target = interface.get_programs(target=target_filter, pagination=None)
        assert len(program1_by_target) == 1, "Should return one program"
        assert program1_by_target[0].program_name == program1.name, "Should return program1"

        # Test pagination
        pagination_filter = PaginationFilter(skip=1, limit=1)
        paginated_programs = interface.get_programs(target=None, pagination=pagination_filter)
        assert len(paginated_programs) == 1, "Should return one program due to pagination"
        assert paginated_programs[0].program_name == program2.name, "Should return program2"


def test_delete_program(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate deleting a program that exists."""
    interface = ProgramsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    # Create a program to delete
    with new_program(vtn_client=vtn_openadr_310_bl_token, program_name="test-program-1") as created_program:
        assert created_program.id is not None, "program should be created successfully"

        # Delete the program
        deleted_program = interface.delete_program_by_id(program_id=created_program.id)

        assert deleted_program.id == created_program.id, "program ID should match"
        assert deleted_program.program_name == created_program.program_name, "program name should match"
        assert deleted_program.program_long_name == created_program.program_long_name, "program long name should match"
        assert deleted_program.retailer_name == created_program.retailer_name, "retailer name should match"
        assert deleted_program.retailer_long_name == created_program.retailer_long_name, "retailer long name should match"
        assert deleted_program.program_type == created_program.program_type, "program type should match"
        assert deleted_program.country == created_program.country, "country should match"
        assert deleted_program.principal_subdivision == created_program.principal_subdivision, "principal subdivision should match"
        assert deleted_program.created_date_time == created_program.created_date_time, "created date time should match"
        assert deleted_program.modification_date_time == created_program.modification_date_time, "modification date time should match"
        assert deleted_program.interval_period == created_program.interval_period, "interval period should match"
        assert deleted_program.payload_descriptors == created_program.payload_descriptors, "payload descriptors should match"
        assert deleted_program.targets == created_program.targets, "targets should match"

    # Verify the program is deleted
    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_program_by_id(program_id=created_program.id)


def test_update_program(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate updating a program that exists."""
    interface = ProgramsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with new_program(vtn_client=vtn_openadr_310_bl_token, program_name="test-program-to-update", targets=("test-target-1",)) as created_program:
        assert created_program.id is not None, "program should be created successfully"

        # Update the program
        program_update = ProgramUpdate(program_name="test-program-updated", targets=("test-value-updated",))

        updated_program = interface.update_program_by_id(program_id=created_program.id, updated_program=created_program.update(program_update))

        # Verify the update
        assert updated_program.program_name == "test-program-updated", "program name should be updated"
        assert updated_program.created_date_time == created_program.created_date_time, "created date time should match"
        assert updated_program.targets is not None, "targets should not be None"
        assert len(updated_program.targets) > 0, "targets should not be empty"
        assert updated_program.targets == ("test-value-updated",), "targets should be updated"
