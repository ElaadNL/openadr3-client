"""Tests the conversion module inside the application module."""

from datetime import datetime, timedelta, timezone
from typing import List
from pydantic import ValidationError
import pytest

from openadr3_client.domain.common.interval_period import IntervalPeriod
from openadr3_client.input_conversion.iterable import (
    EventIntervalDictInput,
    IterableEventIntervalConverter,
)
from openadr3_client.domain.event.event_interval import EventInterval
from openadr3_client.domain.event.event_payload import EventPayload, EventPayloadType


def get_inputs() -> list[list[EventIntervalDictInput]]:
    """Returns a list of dataframe inputs for the test."""
    return [
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "duration": timedelta(hours=1),
                "randomize_start": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            }
        ],
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "duration": timedelta(hours=1),
                "randomize_start": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            },
            {
                "start": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "duration": timedelta(minutes=5),
                "randomize_start": timedelta(minutes=15),
                "type": "PRICE",
                "values": ["test", "test2"],
            },
        ],
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "duration": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            }
        ],
        [{"type": "SIMPLE", "values": [1.0, 2.0]}],
    ]


def get_expected_outputs() -> list[list[EventInterval]]:
    """Returns a list of dataframe outputs for the test."""
    return [
        [
            EventInterval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
                    duration=timedelta(hours=1),
                    randomize_start=timedelta(minutes=5),
                ),
                payloads=(
                    EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),
                ),
            )
        ],
        [
            EventInterval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
                    duration=timedelta(hours=1),
                    randomize_start=timedelta(minutes=5),
                ),
                payloads=(
                    EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),
                ),
            ),
            EventInterval(
                id=1,
                interval_period=IntervalPeriod(
                    start=datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(minutes=15),
                ),
                payloads=(
                    EventPayload(type=EventPayloadType.PRICE, values=("test", "test2")),
                ),
            ),
        ],
        [
            EventInterval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
                    duration=timedelta(minutes=5),
                    randomize_start=None,
                ),
                payloads=(
                    EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),
                ),
            )
        ],
        [
            EventInterval(
                id=0,
                interval_period=None,
                payloads=(
                    EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),
                ),
            )
        ],
    ]


test_cases = list(zip(get_inputs(), get_expected_outputs()))


@pytest.mark.parametrize("input,expected_output", test_cases)
def test_conversion_iterable(
    input: list[EventIntervalDictInput], expected_output: list[EventInterval]
) -> None:
    """Tests the conversion of pandas dataframes to event intervals."""
    converter = IterableEventIntervalConverter()
    intervals_pd = converter.convert(input)
    assert intervals_pd == expected_output


def test_conversion_iterable_no_timezone_offset_datetime() -> None:
    """Tests the conversion of a dataframe with no timezone info in the datetime.

    This action should result in a validation error, at timezone information is required."""
    with pytest.raises(ExceptionGroup) as exception_group:
        input: List[EventIntervalDictInput] = [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=None),
                "duration": timedelta(hours=1),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            }
        ]

        converter = IterableEventIntervalConverter()
        _ = converter.convert(input)

    assert exception_group.group_contains(
        ValidationError, match="validation error for IntervalPeriod\nstart\n"
    )


def test_conversion_iterable_no_payloads_error() -> None:
    """Tests the conversion of a dataframe with no payloads.

    This action should result in a validation error, as atleast a single payload must be present."""
    with pytest.raises(ExceptionGroup) as exception_group:
        input: List[EventIntervalDictInput] = [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                "duration": timedelta(hours=1),
                "type": "SIMPLE",
                "values": [],
            }
        ]

        converter = IterableEventIntervalConverter()
        _ = converter.convert(input)

    assert exception_group.group_contains(
        ValidationError, match="validation error for EventPayload\nvalues\n"
    )
