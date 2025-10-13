import random
import re
import string
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.event.event import NewEvent
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadType


def test_new_event_no_intervals() -> None:
    """Test that validates that intervals are required for new events."""
    with pytest.raises(ValidationError, match=re.escape("NewEvent must contain at least one interval.")):
        _ = NewEvent(
            programID="test-program",
            event_name=None,
            priority=None,
            targets=(),
            payload_descriptors=(),
            interval_period=None,
            intervals=(),
        )


def test_new_event_negative_priority() -> None:
    """Test that validates that a priority must be a positive number for events."""
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        NewEvent(
            programID="test-program",
            event_name=None,
            priority=-1,
            targets=(),
            payload_descriptors=(),
            interval_period=IntervalPeriod(
                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                duration=timedelta(minutes=5),
            ),
            intervals=(
                Interval(
                    id=0,
                    interval_period=None,
                    payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
                ),
            ),
        )


def test_new_event_creation_guard() -> None:
    """
    Test that validates the NewEvent creation guard.

    The NewEvent creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method.
    """
    event = NewEvent(
        programID="test-program",
        event_name=None,
        priority=None,
        targets=(),
        payload_descriptors=(),
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
        ),
        intervals=(
            Interval(
                id=0,
                interval_period=None,
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
            ),
        ),
    )

    with event.with_creation_guard():
        pass  # simply pass through, without an exception.

    with (
        pytest.raises(ValueError, match=re.escape("CreationGuarded object has already been created.")),
        event.with_creation_guard(),
    ):
        pass


def test_event_program_id_too_long() -> None:
    """Test that validates that the program id of an event can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewEvent(
            programID=random_string,
            event_name=None,
            priority=None,
            targets=(),
            payload_descriptors=(),
            interval_period=IntervalPeriod(
                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                duration=timedelta(minutes=5),
            ),
            intervals=(
                Interval(
                    id=0,
                    interval_period=None,
                    payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
                ),
            ),
        )


def test_event_program_id_empty_string() -> None:
    """Test that validates that the program id of an event cannot be an empty string."""
    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewEvent(
            programID="",
            event_name=None,
            priority=None,
            targets=(),
            payload_descriptors=(),
            interval_period=IntervalPeriod(
                start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                duration=timedelta(minutes=5),
            ),
            intervals=(
                Interval(
                    id=0,
                    interval_period=None,
                    payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(2.0, 3.0)),),
                ),
            ),
        )
