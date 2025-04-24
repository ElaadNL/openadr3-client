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