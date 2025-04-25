import pytest
from pydantic import ValidationError

from openadr3_client.domain.event.event_payload import EventPayload, EventPayloadType


def test_event_payload_no_values() -> None:
    """Test that verifies that an event payload with no values raises an error."""
    with pytest.raises(ValidationError, match="payload must contain at least one value"):
        _ = EventPayload(type=EventPayloadType.SIMPLE, values=())
