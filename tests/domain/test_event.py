from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
import pytest

from openadr3_client.domain.common.interval_period import IntervalPeriod
from openadr3_client.domain.event.event import NewEvent
from openadr3_client.domain.event.event_interval import EventInterval
from openadr3_client.domain.event.event_payload import EventPayload, EventPayloadType


def test_new_event_no_intervals() -> None:
    """Test that validates that intervals are required for new events."""
    with pytest.raises(
        ValidationError, match="NewEvent must contain at least one event interval."
    ):
        _ = NewEvent(
            id=None,
            programID="test-program",
            event_name=None,
            priority=None,
            targets=(),
            payload_descriptor=(),
            interval_period=None,
            intervals=(),
        )


def test_new_event_creation_guard() -> None:
    """Test that validates that the NewEvent creation guard.

    The NewEvent creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method."""
    event = NewEvent(
        id=None,
        programID="test-program",
        event_name=None,
        priority=None,
        targets=(),
        payload_descriptor=(),
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            duration=timedelta(minutes=5),
        ),
        intervals=(
            EventInterval(
                id=0,
                interval_period=None,
                payloads=(
                    EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),
                ),
            ),
        ),
    )

    with event.with_creation_guard():
        pass  # simply pass through, without an exception.

    with pytest.raises(ValueError, match="NewEvent has already been created."):
        with event.with_creation_guard():
            pass
