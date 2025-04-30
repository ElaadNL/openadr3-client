"""Tests the events to iterables of dictionaries output conversion module."""

from datetime import UTC, datetime, timedelta

import pytest

from openadr3_client.conversion.common.dict import EventIntervalDictInput
from openadr3_client.conversion.output.events.dict import (
    DictEventIntervalConverter,
)
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadType


def get_inputs() -> list[list[Interval[EventPayload]]]:
    """Returns a list of interval inputs for the test."""
    return [
        [
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(hours=1),
                    randomize_start=timedelta(minutes=5),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),),
            )
        ],
        [
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(hours=1),
                    randomize_start=timedelta(minutes=5),
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),),
            ),
            Interval(
                id=1,
                interval_period=IntervalPeriod(
                    start=datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=timedelta(minutes=15),
                ),
                payloads=(EventPayload(type=EventPayloadType.PRICE, values=("test", "test2")),),
            ),
        ],
        [
            Interval(
                id=0,
                interval_period=IntervalPeriod(
                    start=datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=UTC),
                    duration=timedelta(minutes=5),
                    randomize_start=None,
                ),
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),),
            )
        ],
        [
            Interval(
                id=0,
                interval_period=None,
                payloads=(EventPayload(type=EventPayloadType.SIMPLE, values=(1.0, 2.0)),),
            )
        ],
    ]


def get_expected_outputs() -> list[list[EventIntervalDictInput]]:
    """Returns a list of expected dictionary outputs for the test."""
    return [
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(hours=1),
                "randomize_start": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            }
        ],
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(hours=1),
                "randomize_start": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            },
            {
                "start": datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(minutes=5),
                "randomize_start": timedelta(minutes=15),
                "type": "PRICE",
                "values": ["test", "test2"],
            },
        ],
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
                "randomize_start": None,
            }
        ],
        [
            {
                "type": "SIMPLE",
                "values": [1.0, 2.0],
                "start": None,
                "duration": None,
                "randomize_start": None,
            }
        ],
    ]

test_cases = list(zip(get_inputs(), get_expected_outputs(), strict=False))

@pytest.mark.parametrize(("input", "expected_dict_output"), test_cases)
def test_conversion_iterable(
    input: list[Interval[EventPayload]], expected_dict_output: list[EventIntervalDictInput]
) -> None:
    """Tests the conversion of event intervals to iterables of dictionaries."""
    converter = DictEventIntervalConverter()
    intervals_dict = converter.convert(input)
    assert intervals_dict == expected_dict_output