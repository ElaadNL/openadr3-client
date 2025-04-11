from pydantic import ValidationError
import pytest

from openadr3_client.domain.event.event_payload import EventPayload, EventPayloadType


def test_event_payload_no_values() -> None:
    """Test that verifies that an event payload with no values raises an error."""
    with pytest.raises(
        ValidationError, match="Event payload must contain at least one value"
    ):
        _ = EventPayload(type=EventPayloadType.SIMPLE, values=())


def test_event_no_intervals_defined() -> None:
    """Test that validates that an event with no interval defined on the top level."""
