"""Contains tests for the reports VTN module."""

import pytest
from requests import HTTPError
from openadr3_client._vtn.http.reports import ReportsHttpInterface
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.report.report import ExistingReport, NewReport, ReportResource
from openadr3_client.models.report.report_payload import ReportPayload, ReportPayloadType
from openadr3_client.models.event.event_payload import EventPayloadDescriptor, EventPayloadType
from tests.conftest import IntegrationTestVTNClient

from datetime import UTC, datetime, timedelta, timezone


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
    
    with pytest.raises(HTTPError, match="404 Client Error"):
        tz_aware_dt = datetime.now(tz=timezone.utc)
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
                                payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),)
                            ),
                        )
                    ),
                )
            ))


def test_create_report(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that creating a report in a VTN works correctly."""
    interface = ReportsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    report = NewReport(
        id=None,
        programID="test-program",
        eventID="test-event",
        client_name="test-client",
        report_name="Test Report",
        payload_descriptor=(
            EventPayloadDescriptor(
                payload_type=EventPayloadType.SIMPLE,
                units="kWh",
                currency="EUR"
            ),
        ),
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
                        payloads=(ReportPayload(type=ReportPayloadType.READING, values=(2.0, 3.0)),)
                    ),
                )
            ),
        )
    )

    response = interface.create_report(new_report=report)
    
    assert response.id is not None, "report should be created successfully."
    assert response.program_id == "test-program", "program id should match"
    assert response.event_id == "test-event", "event id should match"
    assert response.client_name == "test-client", "client name should match"
    assert response.report_name == "Test Report", "report name should match" 