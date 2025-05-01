
from typing import Iterable, final

import pandas as pd
from pandera.typing import DataFrame
from openadr3_client.conversion.common.dataframe import EventIntervalDataFrameSchema
from openadr3_client.conversion.output._base_converter import BaseOutputConverter
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.event.event_payload import EventPayload

@final
class PandasEventIntervalConverter(BaseOutputConverter[list[Interval[EventPayload]], DataFrame[EventIntervalDataFrameSchema]]):
    def convert(self, given_input: list[Interval[EventPayload]]) -> DataFrame[EventIntervalDataFrameSchema]:
        """Convert the event intervals to a EventIntervalDataFrameSchema.

        Args:
            given_input (list[Interval[EventPayload]]): The event intervals to convert.

        Returns: The converted event intervals to a EventIntervalDataFrameSchema.
        """
        # Convert the event intervals to a list of dictionaries
        input_as_dicts = [input.model_dump() for input in given_input]

        input_as_dicts = []

        for input in given_input:
            pydantic_as_dict = input.model_dump()

            pydantic_as_dict['payloads'] = [
                {
                    "type": p.type.value,
                    "values": list(p.values)
                }
                for p in input.payloads
            ]

            input_as_dicts.append(pydantic_as_dict)

        # Normalize the dictionaries to a pandas DataFrame
        df = pd.json_normalize(
            input_as_dicts,
            record_path=['payloads'],
            meta=[
                ['interval_period', 'start'],
                ['interval_period', 'duration'],
                ['interval_period', 'randomize_start'],
                'id'
            ],
            errors='ignore' # interval_period in meta might not be present, as it is optional.
        )
        # Rename the columns to match the EventIntervalDataFrameSchema
        df.rename(columns=
                    {'interval_period.start': 'start',
                     'interval_period.duration': 'duration',
                     'interval_period.randomize_start': 'randomize_start'
                    },
                  inplace=True)
        df.reset_index(inplace=True)
        df.set_index("id", inplace=True)
        df.sort_index(inplace=True)
        df.index = df.index.astype(int)
        df['start'] = self._ensure_utc(pd.to_datetime(df['start'], errors='coerce'))

        df['duration'] = pd.to_timedelta(df['duration'], errors='coerce')
        df['randomize_start'] = pd.to_timedelta(df['randomize_start'], errors='coerce')

        return EventIntervalDataFrameSchema.validate(df)
    
    def _ensure_utc(self, series: pd.Series) -> pd.Series:
        """Ensure that the series is in UTC time zone.

        Args:
            series (pd.Series): The series to ensure is in UTC time zone.

        Returns: The series in UTC time zone.
        """
        if series.dt.tz is None:
            # If all values are tz-naive, localize them
            return series.dt.tz_localize("UTC")
        else:
            # If any values are already tz-aware, convert to UTC
            return series.dt.tz_convert("UTC")