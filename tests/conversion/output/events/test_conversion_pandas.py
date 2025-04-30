"""Tests the events to pandas output conversion module."""

from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from openadr3_client.conversion.output.events.pandas import PandasEventIntervalConverter
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadType


def get_inputs() -> list[list[Interval[EventPayload]]]:
    """Returns a list of event interval inputs for the test."""
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


def get_expected_outputs() -> list[pd.DataFrame]:
    """Returns a list of dataframe outputs for the test."""
    return [
        pd.DataFrame(
            {
                "id": 0,
                "start": pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                "duration": pd.Timedelta(hours=1),
                "randomize_start": pd.Timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [[1.0, 2.0]],
            }
        ).set_index("id"),
        pd.DataFrame(
            {
                "id": [0, 1],
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
        ).set_index("id"),
        pd.DataFrame(
            {
                "id": 0,
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
                "randomize_start": [pd.to_timedelta(pd.NaT)],
            }
        ).set_index("id"),
        pd.DataFrame(
            {
                "id": 0,
                "type": [
                    "SIMPLE",
                ],
                "values": [
                    [1.0, 2.0],
                ],
                "start": [None],
                "randomize_start": [pd.to_timedelta(pd.NaT)],
            }
        ).set_index("id"),
    ]


test_cases = list(zip(get_inputs(), get_expected_outputs(), strict=False))


@pytest.mark.parametrize(("input", "expected_df_output"), test_cases)
def test_conversion_pandas(input: list[Interval[EventPayload]], expected_df_output: pd.DataFrame):
    """Tests the conversion of event intervals to pandas dataframes."""
    converter = PandasEventIntervalConverter()
    intervals_pd = converter.convert(input)
    
    # Sort columns alphabetically
    intervals_pd_sorted = intervals_pd[sorted(intervals_pd.columns)]
    expected_df_output_sorted = expected_df_output[sorted(expected_df_output.columns)]

    assert intervals_pd_sorted.equals(expected_df_output_sorted)
