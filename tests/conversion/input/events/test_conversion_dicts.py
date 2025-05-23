"""Tests the conversion module inside the application module."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from openadr3_client.conversion.input.events.dict import (
    DictEventIntervalConverter,
    EventIntervalDictInput,
)
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadType


def get_inputs() -> list[list[EventIntervalDictInput]]:
    """Returns a list of dict inputs for the test."""
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
            }
        ],
        [{"type": "SIMPLE", "values": [1.0, 2.0]}],
    ]


def get_expected_outputs() -> list[list[Interval[EventPayload]]]:
    """Returns a list of dataframe outputs for the test."""
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


test_cases = list(zip(get_inputs(), get_expected_outputs(), strict=False))


@pytest.mark.parametrize(("dict_input", "expected_output"), test_cases)
def test_conversion_iterable(
    dict_input: list[EventIntervalDictInput], expected_output: list[Interval[EventPayload]]
) -> None:
    """Tests the conversion of pandas dataframes to event intervals."""
    converter = DictEventIntervalConverter()
    intervals_pd = converter.convert(dict_input)
    assert intervals_pd == expected_output


def test_conversion_iterable_no_timezone_offset_datetime() -> None:
    """
    Tests the conversion of a dataframe with no timezone info in the datetime.

    This action should result in a validation error, at timezone information is required.
    """
    dict_input: list[EventIntervalDictInput] = [
        {
            "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=None),  # noqa: DTZ001
            "duration": timedelta(hours=1),
            "type": "SIMPLE",
            "values": [1.0, 2.0],
        }
    ]

    converter = DictEventIntervalConverter()

    with pytest.raises(ExceptionGroup) as exception_group:
        _ = converter.convert(dict_input)

    assert exception_group.group_contains(ValidationError, match="validation error for IntervalPeriod\nstart\n")


def test_conversion_iterable_no_payloads_error() -> None:
    """
    Tests the conversion of a dataframe with no payloads.

    This action should result in a validation error, as atleast a single payload must be present.
    """
    dict_input: list[EventIntervalDictInput] = [
        {
            "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            "duration": timedelta(hours=1),
            "type": "SIMPLE",
            "values": [],
        }
    ]

    converter = DictEventIntervalConverter()

    with pytest.raises(ExceptionGroup) as exception_group:
        _ = converter.convert(dict_input)

    assert exception_group.group_contains(ValidationError, match="validation error for EventPayload\nvalues\n")
