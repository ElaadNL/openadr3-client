import random
import string
from typing import Tuple
from pydantic import ValidationError
import pytest
from openadr3_client.domain.common.interval import Interval
from openadr3_client.domain.report.report import NewReport, ReportResource
from openadr3_client.domain.report.report_payload import ReportPayload, ReportPayloadType

def test_new_report_creation_guard() -> None:
    """
    Test that validates the NewReport creation guard.

    The NewReport creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method.
    """
    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )

    resource = ReportResource(resource_name="test-resource", interval_period=None, intervals=(interval,))
    report = NewReport(id=None, programID="my-program", eventID="my-event", client_name="client", resources=(resource,))

    with report.with_creation_guard():
        pass  # simply pass through, without an exception.

    with pytest.raises(ValueError, match="NewReport has already been created."), report.with_creation_guard():
        pass

def test_new_report_no_resources() -> None:
    """
    Test that validates the NewReport with no resources raises a validation error.

    The NewReport creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method.
    """

    with pytest.raises(ValidationError, match="NewReport must contain at least one resource"):
        _ = NewReport(id=None, programID="my-program", eventID="my-event", client_name="client", resources=())

def test_report_program_id_too_long() -> None:
    """Test that validates that the program id of a report can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )

    resource = ReportResource(resource_name="test-resource", interval_period=None, intervals=(interval,))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewReport(id=None, programID=random_string, eventID="my-event", client_name="client", resources=(resource,))


def test_report_program_id_empty_string() -> None:
    """Test that validates that the program id of a report cannot be an empty string."""

    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )

    resource = ReportResource(resource_name="test-resource", interval_period=None, intervals=(interval,))

    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewReport(id=None, programID="", eventID="my-event", client_name="client", resources=(resource,))

def test_report_event_id_too_long() -> None:
    """Test that validates that the event id of a report can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )

    resource = ReportResource(resource_name="test-resource", interval_period=None, intervals=(interval,))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewReport(id=None, programID="my-program", eventID=random_string, client_name="client", resources=(resource,))


def test_report_event_id_empty_string() -> None:
    """Test that validates that the event id of a report cannot be an empty string."""

    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )

    resource = ReportResource(resource_name="test-resource", interval_period=None, intervals=(interval,))

    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewReport(id=None, programID="my-program", eventID="", client_name="client", resources=(resource,))

def test_report_client_name_too_long() -> None:
    """Test that validates that the client name of a report can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )

    resource = ReportResource(resource_name="test-resource", interval_period=None, intervals=(interval,))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewReport(id=None, programID="my-program", eventID="my-event", client_name=random_string, resources=(resource,))


def test_report_client_name_empty_string() -> None:
    """Test that validates that the client name of a report cannot be an empty string."""

    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )

    resource = ReportResource(resource_name="test-resource", interval_period=None, intervals=(interval,))

    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewReport(id=None, programID="my-program", eventID="my-event", client_name="", resources=(resource,))

def test_report_resource_no_intervals() -> None:
    with pytest.raises(ValueError, match="ReportResource must contain at least one interval."):
        _ = ReportResource(resource_name="test-resource", interval_period=None, intervals=())

def test_report_resource_resource_name_too_long() -> None:
    """Test that validates that the resource name of a report cannot be longer than 128 characters."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )
    
    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = ReportResource(resource_name=random_string, interval_period=None, intervals=(interval,))

def test_report_resource_resource_name_empty() -> None:
    """Test that validates that the resource name of a report cannot be an empty string."""
    interval = Interval[ReportPayload[int]](
        id=0,
        interval_period=None,
        payloads=(ReportPayload(type=ReportPayloadType.BASELINE, values=(1,)),),
    )
    
    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = ReportResource(resource_name="", interval_period=None, intervals=(interval,))