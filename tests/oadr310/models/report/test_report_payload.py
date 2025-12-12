import pytest
from pydantic import ValidationError

from openadr3_client.oadr310.models.common.unit import Unit
from openadr3_client.oadr310.models.report.report_payload import (
    ReportPayload,
    ReportPayloadDescriptor,
    ReportPayloadType,
    ReportReadingType,
)


def test_report_payload_no_values() -> None:
    """Test that verifies that a report payload with no values raises an error."""
    with pytest.raises(ValidationError, match="payload must contain at least one value"):
        _ = ReportPayload(type=ReportPayloadType.READING, values=())


def test_report_payload_descriptor_confidence_too_high() -> None:
    """Test that verifies that a report payload descriptor with confidence higher than 100 raises an error."""
    with pytest.raises(ValidationError, match="Input should be less than or equal to 100"):
        _ = ReportPayloadDescriptor(
            payload_type=ReportPayloadType.READING,
            reading_type=ReportReadingType.DIRECT_READ,
            units=Unit.KWH,
            accuracy=2.5,
            confidence=101,
        )


def test_report_payload_descriptor_confidence_toolow() -> None:
    """Test that verifies that a report payload descriptor with confidence lower than 0 raises an error."""
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        _ = ReportPayloadDescriptor(
            payload_type=ReportPayloadType.READING,
            reading_type=ReportReadingType.DIRECT_READ,
            units=Unit.KWH,
            accuracy=2.5,
            confidence=-1,
        )
