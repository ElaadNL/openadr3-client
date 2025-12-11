"""Contains tests for the reports VTN module."""

from datetime import UTC, datetime, timedelta

import pytest
from requests import HTTPError

from openadr3_client._vtn.oadr310.http.reports import ReportsHttpInterface
from openadr3_client.models.oadr310.common.interval import Interval
from openadr3_client.models.oadr310.common.interval_period import IntervalPeriod
from openadr3_client.models.oadr310.report.report import ExistingReport, ReportResource, ReportUpdate
from openadr3_client.models.oadr310.report.report_payload import ReportPayload, ReportPayloadType
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import event_in_program_with_targets, new_program, report_from_ven_in_program, ven_with_targets


def test_get_reports_no_reports_in_vtn(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting reports in a VTN without any reports returns an empty list."""
    interface = ReportsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    response = interface.get_reports(pagination=None, program_id=None, event_id=None, client_name=None)

    assert len(response) == 0, "no reports should be stored in VTN."


def test_get_report_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that getting a report by ID in a VTN with no such report raises an exception."""
    interface = ReportsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        _ = interface.get_report_by_id(report_id="fake-report-id")


def test_delete_report_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that deleting a report by ID in a VTN with no such report raises a 404 error."""
    interface = ReportsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.delete_report_by_id(report_id="fake-report-id")


def test_update_report_by_id_non_existent(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that updating a report by ID in a VTN with no such report raises a 404 error."""
    interface = ReportsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    tz_aware_dt = datetime.now(tz=UTC)
    with pytest.raises(HTTPError, match="404 Client Error"):
        interface.update_report_by_id(
            report_id="fake-report-id",
            updated_report=ExistingReport(
                id="fake-report-id",
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


def test_create_report(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a report in a VTN works correctly."""
    with (
        new_program(vtn_client=vtn_openadr_310_bl_token, program_name="create-report-program") as program,
        ven_with_targets(vtn_client=vtn_openadr_310_bl_token, ven_name="create-report-ven", client_id_of_ven="create-report-ven-client-id") as ven,
        event_in_program_with_targets(vtn_client=vtn_openadr_310_bl_token, program=program, intervals=(), event_name="create-report-test-event") as event,
    ):
        resources = (
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
        )

        with report_from_ven_in_program(vtn_client=vtn_openadr_310_bl_token, ven=ven, event=event, resources=resources) as created_report:
            assert created_report.id is not None, "report should be created successfully"
            assert created_report.event_id == event.id, "event ID should match"
            assert created_report.client_name == ven.ven_name, "client name should match"
            assert created_report.resources is not None and created_report.resources == resources, "resources should match"


def test_get_reports_with_parameters(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate getting reports with various parameter combinations."""
    interface = ReportsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with (
        new_program(vtn_client=vtn_openadr_310_bl_token, program_name="get_reports_with_parameters_program_1") as program1,
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token, ven_name="get_reports_with_parameters_ven_1", client_id_of_ven="get_reports_with_parameters_ven_client_1"
        ) as ven1,
        event_in_program_with_targets(vtn_client=vtn_openadr_310_bl_token, program=program1, intervals=(), event_name="get_reports_with_parameters_event_1") as event1,
        report_from_ven_in_program(vtn_client=vtn_openadr_310_bl_token, ven=ven1, event=event1),
        new_program(vtn_client=vtn_openadr_310_bl_token, program_name="get_reports_with_parameters_program_1") as program2,
        ven_with_targets(
            vtn_client=vtn_openadr_310_bl_token, ven_name="get_reports_with_parameters_ven_2", client_id_of_ven="get_reports_with_parameters_ven_client_2"
        ) as ven2,
        event_in_program_with_targets(vtn_client=vtn_openadr_310_bl_token, program=program2, intervals=(), event_name="get_reports_with_parameters_event_2") as event2,
        report_from_ven_in_program(vtn_client=vtn_openadr_310_bl_token, ven=ven2, event=event2),
    ):
        # Test getting all reports
        all_reports = interface.get_reports(pagination=None, program_id=None, event_id=None, client_name=None)
        assert len(all_reports) == 2, "Should return both reports"

        # Test getting reports by program ID
        program_reports = interface.get_reports(pagination=None, program_id=program1.id, event_id=None, client_name=None)
        assert len(program_reports) == 1, "Should return one report"
        assert program_reports[0].event_id == event1.id, "Should return the correct report"

        # Test getting reports by event ID
        event_reports = interface.get_reports(pagination=None, program_id=None, event_id=event2.id, client_name=None)
        assert len(event_reports) == 1, "Should return one report"
        assert event_reports[0].event_id == event2.id, "Should return the correct report"

        # Test getting reports by client name
        client_reports = interface.get_reports(pagination=None, program_id=None, event_id=None, client_name=ven1.ven_name)
        assert len(client_reports) == 1, "Should return one report"
        assert client_reports[0].client_name == ven1.ven_name, "Should return the correct report"


def test_delete_report(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate deleting a report that exists."""
    interface = ReportsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with (
        new_program(vtn_client=vtn_openadr_310_bl_token, program_name="delete_report_program") as program,
        ven_with_targets(vtn_client=vtn_openadr_310_bl_token, ven_name="delete_report_ven", client_id_of_ven="delete_report_ven_client_id") as ven,
        event_in_program_with_targets(vtn_client=vtn_openadr_310_bl_token, program=program, intervals=(), event_name="delete_report_event") as event,
        report_from_ven_in_program(vtn_client=vtn_openadr_310_bl_token, ven=ven, event=event) as created_report,
    ):
        # Delete the report
        deleted_report = interface.delete_report_by_id(report_id=created_report.id)
        assert deleted_report.id == created_report.id, "Report ID should match"
        assert deleted_report.event_id == event.id, "event ID should match"
        assert deleted_report.client_name == ven.ven_name, "client name should match"

        # Verify the report is deleted
        with pytest.raises(HTTPError, match="404 Client Error"):
            _ = interface.get_report_by_id(report_id=created_report.id)


def test_update_report(vtn_openadr_310_bl_token: IntegrationTestVTNClient) -> None:
    """Test to validate updating a report that exists."""
    interface = ReportsHttpInterface(
        base_url=vtn_openadr_310_bl_token.vtn_base_url,
        config=vtn_openadr_310_bl_token.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    with (
        new_program(vtn_client=vtn_openadr_310_bl_token, program_name="update_report_program") as program,
        ven_with_targets(vtn_client=vtn_openadr_310_bl_token, ven_name="update_report_ven", client_id_of_ven="update_report_ven_client_id") as ven,
        event_in_program_with_targets(vtn_client=vtn_openadr_310_bl_token, program=program, intervals=(), event_name="update_report_event") as event,
        ven_with_targets(vtn_client=vtn_openadr_310_bl_token, ven_name="update_report_ven_2", client_id_of_ven="update_report_ven_client_id_2") as new_ven,
        report_from_ven_in_program(vtn_client=vtn_openadr_310_bl_token, ven=ven, event=event) as created_report,
    ):
        updated_report_resources = (
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
        )

        # Update the report
        report_update = ReportUpdate(
            client_name=new_ven.ven_name,
            resources=updated_report_resources,
        )

        updated_report = interface.update_report_by_id(report_id=created_report.id, updated_report=created_report.update(report_update))

        # Verify the update
        assert updated_report.id == created_report.id, "Report ID should match"
        assert updated_report.event_id == event.id, "event ID should match"
        assert updated_report.client_name == new_ven.ven_name, "client name should be updated"
        assert updated_report.resources is not None and updated_report.resources == updated_report_resources, "Report resources should be equal to update."
