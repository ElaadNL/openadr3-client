"""Contains tests for the programs VTN module."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import AnyHttpUrl
from pydantic_extra_types.country import CountryAlpha2
from pydantic_extra_types.currency_code import ISO4217
from requests.exceptions import HTTPError

from openadr3_client._models.common.interval_period import IntervalPeriod
from openadr3_client.oadr301._vtn.http.programs import ProgramsHttpInterface
from openadr3_client.oadr301._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.oadr301.models.common.target import Target
from openadr3_client.oadr301.models.common.unit import Unit
from openadr3_client.oadr301.models.event.event_payload import EventPayloadDescriptor, EventPayloadType
from openadr3_client.oadr301.models.program.program import ExistingProgram, NewProgram, ProgramDescription, ProgramUpdate
from tests.conftest import IntegrationTestVTNClient


def test_get_programs_no_programs_in_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting programs in a VTN without any programs returns an empty list."""
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    response = interface.get_programs(target=None, pagination=None)

    assert len(response) == 0, "no programs should be stored in VTN."


def test_get_program_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a program by ID in a VTN with no such program raises an exception."""
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_program_by_id(program_id="fake-program-id")


def test_delete_program_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a program by ID in a VTN with no such program raises a 404 error."""
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_program_by_id(program_id="fake-program-id")


def test_update_program_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a program by ID in a VTN with no such program raises a 404 error."""
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
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
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                ),
                payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
            ),
        )


def test_create_program(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a program in a VTN works correctly."""
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    program = NewProgram(
        program_name="Test Program",
        program_long_name="Test Program Long Name",
        retailer_name="Test Retailer Name",
        retailer_long_name="Test Retailer Long Name",
        program_type="Test Program Type",
        country=CountryAlpha2("NL"),
        principal_subdivision="NB",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
            randomize_start=timedelta(minutes=5),
        ),
        payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
        program_descriptions=(ProgramDescription(url=AnyHttpUrl("https://example.com")),),
        binding_events=True,
        local_price=True,
        targets=(Target(type="test-target", values=("test-value",)),),
    )

    try:
        response = interface.create_program(new_program=program)

        assert response.id is not None, "program should be created successfully."
        assert response.program_name == "Test Program", "program name should match"
        assert response.program_long_name == "Test Program Long Name", "program long name should match"
        assert response.retailer_name == "Test Retailer Name", "retailer name should match"
        assert response.retailer_long_name == "Test Retailer Long Name", "retailer long name should match"
        assert response.program_type == "Test Program Type", "program type should match"
        assert response.country == "NL", "country should match"
        assert response.principal_subdivision == "NB", "principal subdivision should match"
        assert response.interval_period == IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
            randomize_start=timedelta(minutes=5),
        ), "interval period should match"
        assert response.payload_descriptors == (EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),), (
            "payload descriptors should match"
        )
        assert response.program_descriptions == (ProgramDescription(url=AnyHttpUrl("https://example.com")),), "program descriptions should match"
        assert response.binding_events is True, "binding events should match"
        assert response.local_price is True, "local price should match"
        assert response.targets == (Target(type="test-target", values=("test-value",)),), "targets should match"
    finally:
        interface.delete_program_by_id(program_id=response.id)


def test_get_programs_with_parameters(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate getting programs with various parameter combinations."""
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # Create two programs with different names and targets
    program1 = NewProgram(
        program_name="test-program-1",
        program_long_name="Test Program 1 Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
        targets=(Target(type="test-target-1", values=("test-value-1",)),),
    )
    program2 = NewProgram(
        program_name="test-program-2",
        program_long_name="Test Program 2 Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
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
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # Create a program to delete
    program = NewProgram(
        program_name="test-program-to-delete",
        program_long_name="Test Program To Delete Long Name",
        retailer_name="Test Retailer Name",
        retailer_long_name="Test Retailer Long Name",
        program_type="Test Program Type",
        country=CountryAlpha2("NL"),
        principal_subdivision="NB",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
        targets=(Target(type="test-target", values=("test-value",)),),
        program_descriptions=(ProgramDescription(url=AnyHttpUrl("https://example.com")),),
        binding_events=True,
        local_price=True,
    )
    created_program = interface.create_program(new_program=program)
    assert created_program.id is not None, "program should be created successfully"

    # Delete the program
    deleted_program = interface.delete_program_by_id(program_id=created_program.id)

    assert deleted_program.id == created_program.id, "program ID should match"
    assert deleted_program.program_name == "test-program-to-delete", "program name should match"
    assert deleted_program.program_long_name == "Test Program To Delete Long Name", "program long name should match"
    assert deleted_program.retailer_name == "Test Retailer Name", "retailer name should match"
    assert deleted_program.retailer_long_name == "Test Retailer Long Name", "retailer long name should match"
    assert deleted_program.program_type == "Test Program Type", "program type should match"
    assert deleted_program.country == "NL", "country should match"
    assert deleted_program.principal_subdivision == "NB", "principal subdivision should match"
    assert deleted_program.created_date_time == created_program.created_date_time, "created date time should match"
    assert deleted_program.modification_date_time == created_program.modification_date_time, "modification date time should match"
    assert deleted_program.interval_period == created_program.interval_period, "interval period should match"
    assert deleted_program.payload_descriptors == created_program.payload_descriptors, "payload descriptors should match"
    assert deleted_program.targets == created_program.targets, "targets should match"

    # Verify the program is deleted
    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_program_by_id(program_id=created_program.id)


def test_update_program(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate updating a program that exists."""
    interface = ProgramsHttpInterface(
        base_url=integration_test_vtn_client.vtn_base_url,
        config=integration_test_vtn_client.config,
    )

    # Create a program to update
    program = NewProgram(
        program_name="test-program-to-update",
        program_long_name="Test Program To Update Long Name",
        retailer_name="Test Retailer Name",
        retailer_long_name="Test Retailer Long Name",
        program_type="Test Program Type",
        country=CountryAlpha2("NL"),
        principal_subdivision="NB",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
        targets=(Target(type="test-target", values=("test-value",)),),
        program_descriptions=(ProgramDescription(url=AnyHttpUrl("https://example.com")),),
        binding_events=True,
        local_price=True,
    )
    created_program = interface.create_program(new_program=program)
    assert created_program.id is not None, "program should be created successfully"

    try:
        # Update the program
        program_update = ProgramUpdate(
            program_name="test-program-updated",
            program_long_name="Test Program Updated Long Name",
            retailer_name="Test Retailer Name Updated",
            retailer_long_name="Test Retailer Long Name Updated",
            program_type="Test Program Type Updated",
            country=CountryAlpha2("NL"),
            principal_subdivision="NB",
            interval_period=IntervalPeriod(
                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                duration=timedelta(minutes=5),
            ),
            payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
            program_descriptions=(ProgramDescription(url=AnyHttpUrl("https://example.com")),),
            binding_events=True,
            local_price=True,
            targets=(Target(type="test-target-updated", values=("test-value-updated",)),),
        )

        updated_program = interface.update_program_by_id(program_id=created_program.id, updated_program=created_program.update(program_update))

        # Verify the update
        assert updated_program.program_name == "test-program-updated", "program name should be updated"
        assert updated_program.program_long_name == "Test Program Updated Long Name", "program long name should be updated"
        assert updated_program.retailer_name == "Test Retailer Name Updated", "retailer name should be updated"
        assert updated_program.retailer_long_name == "Test Retailer Long Name Updated", "retailer long name should be updated"
        assert updated_program.program_type == "Test Program Type Updated", "program type should be updated"
        assert updated_program.country == CountryAlpha2("NL"), "country should be updated"
        assert updated_program.created_date_time == created_program.created_date_time, "created date time should match"
        assert updated_program.modification_date_time != created_program.modification_date_time, "modification date time should not match"
        assert updated_program.targets is not None, "targets should not be None"
        assert len(updated_program.targets) > 0, "targets should not be empty"
        assert updated_program.targets[0].type == "test-target-updated", "target type should be updated"
        assert updated_program.targets[0].values == ("test-value-updated",), "target values should be updated"
    finally:
        interface.delete_program_by_id(program_id=created_program.id)
