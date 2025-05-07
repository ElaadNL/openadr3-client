"""Contains tests for the reports VTN module."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic_extra_types.currency_code import ISO4217
from requests import HTTPError

from openadr3_client._vtn.http.events import EventsHttpInterface
from openadr3_client._vtn.http.programs import ProgramsHttpInterface
from openadr3_client._vtn.http.reports import ReportsHttpInterface
from openadr3_client._vtn.http.vens import VensHttpInterface
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.common.unit import Unit
from openadr3_client.models.event.event import NewEvent
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadDescriptor, EventPayloadType
from openadr3_client.models.program.program import NewProgram
from openadr3_client.models.report.report import ExistingReport, NewReport, ReportResource, ReportUpdate
from openadr3_client.models.report.report_payload import ReportPayload, ReportPayloadType
from openadr3_client.models.ven.ven import NewVen
from tests.conftest import IntegrationTestVTNClient


def test_get_reports_no_reports_in_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting reports in a VTN without any reports returns an empty list."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    response = interface.get_reports(pagination=None, program_id=None, event_id=None, client_name=None)

    assert len(response) == 0, "no reports should be stored in VTN."


def test_get_report_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a report by ID in a VTN with no such report raises an exception."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_report_by_id(report_id="fake-report-id")


def test_delete_report_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a report by ID in a VTN with no such report raises a 404 error."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_report_by_id(report_id="fake-report-id")


def test_update_report_by_id_non_existent(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a report by ID in a VTN with no such report raises a 404 error."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    tz_aware_dt = datetime.now(tz=UTC)
    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.update_report_by_id(
            report_id="fake-report-id",
            updated_report=ExistingReport(
                id="fake-report-id",
                programID="test-program",
                eventID="test-event",
                client_name="test-client",
                created_date_time=tz_aware_dt,
                modification_date_time=tz_aware_dt,
                resources=(
                    ReportResource(
                        resource_name="test-resource",
                        interval_period=IntervalPeriod(
                            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                            duration=timedelta(minutes=5),
                        ),
                        intervals=(
                            Interval(
                                id=0,
                                interval_period=None,
                                payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),),
                            ),
                        ),
                    ),
                ),
            ),
        )


def test_create_report(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a report in a VTN works correctly."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    programs_interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    events_interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    vens_interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # First create a program
    program = NewProgram(
        program_name="test-program",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
    )
    created_program = programs_interface.create_program(new_program=program)
    assert created_program.id is not None, "program should be created successfully"

    try:
        # Create an event that belongs to the program
        event = NewEvent(
            programID=created_program.id,
            event_name="test-event",
            priority=1,
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
        created_event = events_interface.create_event(new_event=event)
        assert created_event.id is not None, "event should be created successfully"

        try:
            # Create a VEN with the same name as the client_name
            ven = NewVen(
                ven_name="test-client",
                targets=(),
            )
            created_ven = vens_interface.create_ven(new_ven=ven)
            assert created_ven.id is not None, "VEN should be created successfully"

            try:
                # Now create the report
                report = NewReport(
                    programID=created_program.id,
                    eventID=created_event.id,
                    client_name="test-client",
                    resources=(
                        ReportResource(
                            resource_name="test-resource",
                            interval_period=IntervalPeriod(
                                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                                duration=timedelta(minutes=5),
                            ),
                            intervals=(
                                Interval(
                                    id=0,
                                    interval_period=None,
                                    payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),),
                                ),
                            ),
                        ),
                    ),
                )

                response = interface.create_report(new_report=report)

                assert response.id is not None, "report should be created successfully"
                assert response.program_id == created_program.id, "program ID should match"
                assert response.event_id == created_event.id, "event ID should match"
                assert response.client_name == "test-client", "client name should match"
                assert response.resources is not None and len(response.resources) == 1, "resources should match"

                interface.delete_report_by_id(report_id=response.id)
            finally:
                vens_interface.delete_ven_by_id(ven_id=created_ven.id)
        finally:
            events_interface.delete_event_by_id(event_id=created_event.id)
    finally:
        programs_interface.delete_program_by_id(program_id=created_program.id)


def test_get_reports_with_parameters(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate getting reports with various parameter combinations."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    programs_interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    events_interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    vens_interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # Create two programs
    program1 = NewProgram(
        program_name="test-program-1",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
    )
    program2 = NewProgram(
        program_name="test-program-2",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
    )
    created_program1 = programs_interface.create_program(new_program=program1)
    created_program2 = programs_interface.create_program(new_program=program2)

    try:
        # Create two events
        event1 = NewEvent(
            programID=created_program1.id,
            event_name="test-event-1",
            priority=1,
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
        event2 = NewEvent(
            programID=created_program2.id,
            event_name="test-event-2",
            priority=1,
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
        created_event1 = events_interface.create_event(new_event=event1)
        created_event2 = events_interface.create_event(new_event=event2)

        try:
            # Create two VENs
            ven1 = NewVen(
                ven_name="test-client-1",
                targets=(),
            )
            ven2 = NewVen(
                ven_name="test-client-2",
                targets=(),
            )
            created_ven1 = vens_interface.create_ven(new_ven=ven1)
            created_ven2 = vens_interface.create_ven(new_ven=ven2)

            try:
                # Create two reports with different parameters
                report1 = NewReport(
                    programID=created_program1.id,
                    eventID=created_event1.id,
                    client_name=created_ven1.ven_name,
                    resources=(
                        ReportResource(
                            resource_name="test-resource-1",
                            interval_period=IntervalPeriod(
                                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                                duration=timedelta(minutes=5),
                            ),
                            intervals=(
                                Interval(
                                    id=0,
                                    interval_period=None,
                                    payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),),
                                ),
                            ),
                        ),
                    ),
                )
                report2 = NewReport(
                    programID=created_program2.id,
                    eventID=created_event2.id,
                    client_name=created_ven2.ven_name,
                    resources=(
                        ReportResource(
                            resource_name="test-resource-2",
                            interval_period=IntervalPeriod(
                                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                                duration=timedelta(minutes=5),
                            ),
                            intervals=(
                                Interval(
                                    id=0,
                                    interval_period=None,
                                    payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),),
                                ),
                            ),
                        ),
                    ),
                )
                created_report1 = interface.create_report(new_report=report1)
                created_report2 = interface.create_report(new_report=report2)

                try:
                    # Test getting all reports
                    all_reports = interface.get_reports(
                        pagination=None, program_id=None, event_id=None, client_name=None
                    )
                    assert len(all_reports) == 2, "Should return both reports"

                    # Test getting reports by program ID
                    program_reports = interface.get_reports(
                        pagination=None, program_id=created_program1.id, event_id=None, client_name=None
                    )
                    assert len(program_reports) == 1, "Should return one report"
                    assert program_reports[0].program_id == created_program1.id, "Should return the correct report"

                    # Test getting reports by event ID
                    event_reports = interface.get_reports(
                        pagination=None, program_id=None, event_id=created_event2.id, client_name=None
                    )
                    assert len(event_reports) == 1, "Should return one report"
                    assert event_reports[0].event_id == created_event2.id, "Should return the correct report"

                    # Test getting reports by client name
                    client_reports = interface.get_reports(
                        pagination=None, program_id=None, event_id=None, client_name=created_ven1.ven_name
                    )
                    assert len(client_reports) == 1, "Should return one report"
                    assert client_reports[0].client_name == created_ven1.ven_name, "Should return the correct report"
                finally:
                    interface.delete_report_by_id(report_id=created_report1.id)
                    interface.delete_report_by_id(report_id=created_report2.id)
            finally:
                vens_interface.delete_ven_by_id(ven_id=created_ven1.id)
                vens_interface.delete_ven_by_id(ven_id=created_ven2.id)
        finally:
            events_interface.delete_event_by_id(event_id=created_event1.id)
            events_interface.delete_event_by_id(event_id=created_event2.id)
    finally:
        programs_interface.delete_program_by_id(program_id=created_program1.id)
        programs_interface.delete_program_by_id(program_id=created_program2.id)


def test_delete_report(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate deleting a report that exists."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    programs_interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    events_interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    vens_interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # Create a program
    program = NewProgram(
        program_name="test-program",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
    )
    created_program = programs_interface.create_program(new_program=program)
    assert created_program.id is not None, "program should be created successfully"

    try:
        # Create an event
        event = NewEvent(
            programID=created_program.id,
            event_name="test-event",
            priority=1,
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
        created_event = events_interface.create_event(new_event=event)
        assert created_event.id is not None, "event should be created successfully"

        try:
            # Create a VEN
            ven = NewVen(
                ven_name="test-client",
                targets=(),
            )
            created_ven = vens_interface.create_ven(new_ven=ven)
            assert created_ven.id is not None, "VEN should be created successfully"

            try:
                # Create a report to delete
                report = NewReport(
                    programID=created_program.id,
                    eventID=created_event.id,
                    client_name="test-client",
                    resources=(
                        ReportResource(
                            resource_name="test-resource",
                            interval_period=IntervalPeriod(
                                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                                duration=timedelta(minutes=5),
                            ),
                            intervals=(
                                Interval(
                                    id=0,
                                    interval_period=None,
                                    payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),),
                                ),
                            ),
                        ),
                    ),
                )
                created_report = interface.create_report(new_report=report)
                assert created_report.id is not None, "report should be created successfully"

                # Delete the report
                interface.delete_report_by_id(report_id=created_report.id)

                # Verify the report is deleted
                with pytest.raises(HTTPError, match="404 Client Error"):
                    _ = interface.get_report_by_id(report_id=created_report.id)
            finally:
                vens_interface.delete_ven_by_id(ven_id=created_ven.id)
        finally:
            events_interface.delete_event_by_id(event_id=created_event.id)
    finally:
        programs_interface.delete_program_by_id(program_id=created_program.id)


def test_update_report(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate updating a report that exists."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    programs_interface = ProgramsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    events_interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    vens_interface = VensHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    # Create a program
    program = NewProgram(
        program_name="test-program",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        payload_descriptor=(
            EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),
        ),
    )
    created_program = programs_interface.create_program(new_program=program)
    assert created_program.id is not None, "program should be created successfully"

    try:
        # Create an event
        event = NewEvent(
            programID=created_program.id,
            event_name="test-event",
            priority=1,
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
        created_event = events_interface.create_event(new_event=event)
        assert created_event.id is not None, "event should be created successfully"

        try:
            # Create a VEN
            ven = NewVen(
                ven_name="test-client",
                targets=(),
            )
            created_ven = vens_interface.create_ven(new_ven=ven)
            assert created_ven.id is not None, "VEN should be created successfully"

            try:
                # Create a report to update
                report = NewReport(
                    programID=created_program.id,
                    eventID=created_event.id,
                    client_name="test-client",
                    resources=(
                        ReportResource(
                            resource_name="test-resource",
                            interval_period=IntervalPeriod(
                                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                                duration=timedelta(minutes=5),
                            ),
                            intervals=(
                                Interval(
                                    id=0,
                                    interval_period=None,
                                    payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),),
                                ),
                            ),
                        ),
                    ),
                )
                created_report = interface.create_report(new_report=report)
                assert created_report.id is not None, "report should be created successfully"

                try:
                    # Update the report
                    report_update = ReportUpdate(
                        client_name="test-client-updated",
                        resources=(
                            ReportResource(
                                resource_name="test-resource-updated",
                                interval_period=IntervalPeriod(
                                    start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                                    duration=timedelta(minutes=5),
                                ),
                                intervals=(
                                    Interval(
                                        id=0,
                                        interval_period=None,
                                        payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),),
                                    ),
                                ),
                            ),
                        ),
                    )

                    updated_report = interface.update_report_by_id(
                        report_id=created_report.id, updated_report=created_report.update(report_update)
                    )

                    # Verify the update
                    assert updated_report.program_id == created_program.id, "program ID should match"
                    assert updated_report.event_id == created_event.id, "event ID should match"
                    assert updated_report.client_name == "test-client-updated", "client name should be updated"
                    assert updated_report.created_date_time == created_report.created_date_time, (
                        "created date time should match"
                    )
                    assert updated_report.modification_date_time != created_report.modification_date_time, (
                        "modification date time should not match"
                    )
                    assert updated_report.resources is not None, "resources should not be None"
                    assert len(updated_report.resources) > 0, "resources should not be empty"
                    assert updated_report.resources[0].resource_name == "test-resource-updated", (
                        "resource name should be updated"
                    )
                finally:
                    interface.delete_report_by_id(report_id=created_report.id)
            finally:
                vens_interface.delete_ven_by_id(ven_id=created_ven.id)
        finally:
            events_interface.delete_event_by_id(event_id=created_event.id)
    finally:
        programs_interface.delete_program_by_id(program_id=created_program.id)
