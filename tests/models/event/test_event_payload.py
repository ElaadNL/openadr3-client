import pytest
from pydantic import ValidationError

from openadr3_client.models.common.unit import Unit
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadDescriptor, EventPayloadType


def test_event_payload_no_values() -> None:
    """Test that verifies that an event payload with no values raises an error."""
    with pytest.raises(ValidationError, match="payload must contain at least one value"):
        _ = EventPayload(type=EventPayloadType.SIMPLE, values=())


def test_event_payload_descriptor_custom_unit() -> None:
    """
    Test that verifies that an event payload descriptor with a custom unit is allowed.

    Note that using a custom enum case requires the functional constructor.
    """
    descriptor = EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit("CUSTOM"))
    assert descriptor.units == "CUSTOM"
