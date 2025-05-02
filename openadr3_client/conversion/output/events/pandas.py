from typing import final

import pandas as pd
from pandera.typing import DataFrame

from openadr3_client.conversion.common.dataframe import EventIntervalDataFrameSchema
from openadr3_client.conversion.output._base_converter import BaseOutputConverter
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.event.event_payload import EventPayload


@final
class PandasEventIntervalConverter(
    BaseOutputConverter[list[Interval[EventPayload]], DataFrame[EventIntervalDataFrameSchema]]
):
    """Class which can convert a list of event intervals to a pandas DataFrame."""

    def convert(self, given_input: list[Interval[EventPayload]]) -> DataFrame[EventIntervalDataFrameSchema]:
        """
        Convert the event intervals to a EventIntervalDataFrameSchema.

        Args:
            given_input (list[Interval[EventPayload]]): The event intervals to convert.

        Returns: The converted event intervals to a EventIntervalDataFrameSchema.

        """
        input_as_dicts = []

        for interval in given_input:
            pydantic_as_dict = interval.model_dump()

            pydantic_as_dict["payloads"] = [{"type": p.type.value, "values": list(p.values)} for p in interval.payloads]

            input_as_dicts.append(pydantic_as_dict)

        # Normalize the dictionaries to a pandas DataFrame
        intervals_as_df = pd.json_normalize(
            input_as_dicts,
            record_path=["payloads"],
            meta=[
                ["interval_period", "start"],
                ["interval_period", "duration"],
                ["interval_period", "randomize_start"],
                "id",
            ],
            errors="ignore",  # interval_period in meta might not be present, as it is optional.
        )
        # Rename the columns to match the EventIntervalDataFrameSchema
        intervals_as_df = intervals_as_df.rename(
            columns={
                "interval_period.start": "start",
                "interval_period.duration": "duration",
                "interval_period.randomize_start": "randomize_start",
            },
        )
        intervals_as_df = intervals_as_df.reset_index()
        intervals_as_df = intervals_as_df.set_index("id")
        intervals_as_df = intervals_as_df.sort_index()
        intervals_as_df.index = intervals_as_df.index.astype(int)
        intervals_as_df["start"] = self._ensure_utc(pd.to_datetime(intervals_as_df["start"], errors="coerce"))

        intervals_as_df["duration"] = pd.to_timedelta(intervals_as_df["duration"], errors="coerce")
        intervals_as_df["randomize_start"] = pd.to_timedelta(intervals_as_df["randomize_start"], errors="coerce")

        return EventIntervalDataFrameSchema.validate(intervals_as_df)

    def _ensure_utc(self, series: pd.Series) -> pd.Series:
        """
        Ensure that the series is in UTC time zone.

        Args:
            series (pd.Series): The series to ensure is in UTC time zone.

        Returns: The series in UTC time zone.

        """
        if series.dt.tz is None:
            # If all values are tz-naive, localize them
            return series.dt.tz_localize("UTC")
        # If any values are already tz-aware, convert to UTC
        return series.dt.tz_convert("UTC")
