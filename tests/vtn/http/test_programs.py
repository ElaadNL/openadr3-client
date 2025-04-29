"""Contains tests for the programs VTN module."""

import pytest
from requests import HTTPError
from openadr3_client._vtn.http.programs import ProgramsHttpInterface
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.program.program import ExistingProgram, NewProgram
from openadr3_client.models.event.event_payload import EventPayloadDescriptor, EventPayloadType
from tests.conftest import IntegrationTestVTNClient

from datetime import UTC, datetime, timedelta, timezone


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
    
    with pytest.raises(HTTPError, match="404 Client Error"):
        tz_aware_dt = datetime.now(tz=timezone.utc)
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
                payload_descriptor=(EventPayloadDescriptor(
                    payload_type=EventPayloadType.SIMPLE,
                    units="kWh",
                    currency="EUR"
                ),)
            ))


def test_create_program(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a program in a VTN works correctly."""
    interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    program = NewProgram(
        id=None,
        program_name="Test Program",
        program_long_name="Test Program Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(EventPayloadDescriptor(
            payload_type=EventPayloadType.SIMPLE,
            units="kWh",
            currency="EUR"
        ),)
    )

    response = interface.create_program(new_program=program)
    
    assert response.id is not None, "program should be created successfully."
    assert response.program_name == "Test Program", "program name should match"
    assert response.program_long_name == "Test Program Long Name", "program long name should match" 