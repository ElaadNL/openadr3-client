"""Tests the conversion module inside the application module."""

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest
from pandera.errors import ParserError, SchemaError

from openadr3_client.oadr310.conversion.input.events.pandas import PandasEventIntervalConverter
from openadr3_client._models.common.interval import Interval
from openadr3_client._models.common.interval_period import IntervalPeriod
from openadr3_client.oadr310.models.event.event_payload import EventPayload, EventPayloadType


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


@pytest.mark.parametrize(("df_input", "expected_output"), test_cases)
def test_conversion_pandas(df_input: pd.DataFrame, expected_output: list[Interval[EventPayload]]):
    """Tests the conversion of pandas dataframes to event intervals."""
    converter = PandasEventIntervalConverter()
    intervals_pd = converter.convert(df_input)
    assert intervals_pd == expected_output


def test_conversion_pandas_no_timezone_offset_datetime():
    """
    Tests the conversion of a dataframe with no timezone info in the datetime.

    This action should result in a validation error, at timezone information is required.
    """
    df_input = pd.DataFrame(
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

    converter = PandasEventIntervalConverter()

    with pytest.raises(ExceptionGroup) as exception_group:
        _ = converter.convert(df_input)

    assert exception_group.group_contains(ParserError, match="When time_zone_agnostic=True, data must either be")


def test_conversion_pandas_no_payloads_error():
    """
    Tests the conversion of a dataframe with no payloads.

    This action should result in a validation error, as atleast a single payload must be present.
    """
    df_input = pd.DataFrame(
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

    converter = PandasEventIntervalConverter()

    with pytest.raises(ExceptionGroup) as exception_group:
        _ = converter.convert(df_input)

    assert exception_group.group_contains(SchemaError, match="payload_values_atleast_one")
