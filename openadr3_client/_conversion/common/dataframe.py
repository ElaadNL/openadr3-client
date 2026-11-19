# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from typing import final

try:
    import pandas as pd
    import pandera.pandas as pa
    from pandera.engines.pandas_engine import DateTime
    from pandera.typing import Series, Timedelta
except ImportError as e:
    msg = "DataFrame conversion functionality requires the 'pandas' extra. Install it with: pip install 'openadr3-client[pandas]' or the equivalent in your package manager."
    raise ImportError(msg) from e

# Resolution used for datetime and timedelta columns. Microseconds is the pandas 3 default
# for python datetime/timedelta objects, and matches the precision of the pydantic models.
DATETIME_UNIT = "us"


@final
class EventIntervalDataFrameSchema(pa.DataFrameModel):
    """
    Pandera schema for an event interval dataframe.

    Datetime and timedelta columns of any resolution are accepted; the validated dataframe
    returned by `validate` always has them in microsecond resolution.
    """

    # IntervalPeriod fields (flattened)
    start: Series[DateTime(unit=DATETIME_UNIT, time_zone_agnostic=True)] | None = pa.Field(nullable=True)  # type: ignore[reportInvalidTypeForm, valid-type]
    duration: Series[Timedelta] | None = pa.Field(nullable=True)
    randomize_start: Series[Timedelta] | None = pa.Field(nullable=True)

    # EventPayload fields (flattened)
    type: Series[str] = pa.Field()  # Enum type not directly supported with pandera, but pydantic will validate this later on.
    values: Series[pa.Object] = pa.Field()  # Type validation will be done by pydantic later.

    class Config:
        strict = "filter"  # Filter out any columns not specified in the schema here.

    @pa.parser("start", "duration", "randomize_start")
    @classmethod
    def as_datetime_unit(cls, series: pd.Series) -> pd.Series:
        """Normalize datetime and timedelta columns to a single resolution, regardless of the input resolution."""
        if pd.api.types.is_datetime64_any_dtype(series) or pd.api.types.is_timedelta64_dtype(series):
            return series.dt.as_unit(DATETIME_UNIT)
        return series

    @pa.parser("type")
    @classmethod
    def object_as_str(cls, series: pd.Series) -> pd.Series:
        """Accept legacy object dtype string columns, by converting them to the pandas 3 str dtype."""
        if pd.api.types.is_object_dtype(series):
            return series.astype("str")
        return series

    @pa.check("values")
    def payload_values_atleast_one(self, values: Series) -> Series[bool]:
        """Check that the values are a list and have at least one element."""
        return values.map(lambda v: isinstance(v, list) and len(v) > 0)  # type: ignore[return-value]
