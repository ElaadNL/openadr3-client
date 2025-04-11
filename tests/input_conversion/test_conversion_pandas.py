"""Tests the conversion module inside the application module."""

from datetime import datetime, timedelta, timezone
import pandas as pd
import pytest
from pandera.errors import SchemaError, ParserError


from openadr3_client.input_conversion.pandas import DataFrameEventIntervalConverter
from openadr3_client.domain.event.event_interval import EventInterval, IntervalPeriod
from openadr3_client.domain.event.event_payload import EventPayload, EventPayloadType


def get_inputs() -> list[pd.DataFrame]:
    """Returns a list of dataframe inputs for the test."""
    return [
        pd.DataFrame(
            {
                "start": pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                "duration": pd.Timedelta(hours=1),
                "randomize_start": pd.Timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [[1.0, 2.0]],
            }
        ),
        pd.DataFrame(
            {
                "start": [
                    pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                    pd.Timestamp("2024-01-01 00:00:00.000Z").as_unit("ns"),
                ],
                "duration": [pd.Timedelta(hours=1), pd.Timedelta(minutes=5)],
                "randomize_start": [
                    pd.Timedelta(minutes=5),
                    pd.Timedelta(minutes=15),
                ],
                "type": ["SIMPLE", "PRICE"],
                "values": [[1.0, 2.0], ["test", "test2"]],
            }
        ),
        pd.DataFrame(
            {
                "start": [
                    pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                ],
                "duration": [pd.Timedelta(minutes=5)],
                "type": [
                    "SIMPLE",
                ],
                "values": [
                    [1.0, 2.0],
                ],
            }
        ),
        pd.DataFrame(
            {
                "type": [
                    "SIMPLE",
                ],
                "values": [
                    [1.0, 2.0],
                ],
            }
        ),
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
def test_conversion_pandas(input: pd.DataFrame, expected_output: list[EventInterval]):
    """Tests the conversion of pandas dataframes to event intervals."""
    converter = DataFrameEventIntervalConverter()
    intervals_pd = converter.convert(input)
    assert intervals_pd == expected_output


def test_conversion_pandas_no_timezone_offset_datetime():
    """Tests the conversion of a dataframe with no timezone info in the datetime.

    This action should result in a validation error, at timezone information is required."""
    with pytest.raises(ExceptionGroup) as exception_group:
        input = pd.DataFrame(
            {
                "start": [pd.Timestamp("2023-01-01 00:00:00.000").as_unit("ns")],
                "duration": [pd.Timedelta(minutes=5)],
                "type": ["SIMPLE"],
                "values": [
                    [1.0, 2.0],
                ],
            },
            index=[0],
        )

        converter = DataFrameEventIntervalConverter()
        _ = converter.convert(input)

    assert exception_group.group_contains(
        ParserError, match="When time_zone_agnostic=True, data must either be"
    )


def test_conversion_pandas_no_payloads_error():
    """Tests the conversion of a dataframe with no payloads.

    This action should result in a validation error, as atleast a single payload must be present."""
    with pytest.raises(ExceptionGroup) as exception_group:
        input = pd.DataFrame(
            {
                "start": pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                "duration": [pd.Timedelta(minutes=5)],
                "type": "SIMPLE",
                # Dataframes already validate that the count of values must be equal.
                # So we validate on a 'malicious compliance' case, in which a value is provided
                # that does not represent a value.
                "values": [""],
            },
            index=[0],
        )

        converter = DataFrameEventIntervalConverter()
        _ = converter.convert(input)

    assert exception_group.group_contains(
        SchemaError, match="payload_values_atleast_one"
    )
