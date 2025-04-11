from pydantic import ValidationError
import pytest

from openadr3_client.domain.event.event_interval import EventInterval


def test_event_interval_no_payloads() -> None:
    """Test that verifies that an event interval with no payload raises an error."""
    with pytest.raises(
        ValidationError,
        match="Event interval payload must contain at least one payload",
    ):
        _ = EventInterval(id=0, interval_period=None, payloads=())
