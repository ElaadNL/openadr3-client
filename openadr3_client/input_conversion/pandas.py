"""Module containing the conversion logic for Pandas dataframes"""

from typing import Any, Hashable, Optional
import pandas as pd
import pandera as pa
from pandera.typing import Series, Timedelta
from pandera.engines.pandas_engine import DateTime

from openadr3_client.input_conversion._base_converter import (
    ERROR,
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)


class _EventIntervalDataFrameSchema(pa.DataFrameModel):
    # IntervalPeriod fields (flattened)
    # time_zone_agnostic datetime available as of https://github.com/unionai-oss/pandera/pull/1902
    start: Optional[Series[DateTime(time_zone_agnostic=True)]]  # type: ignore
    duration: Optional[Series[Timedelta]]
    randomize_start: Optional[Series[Timedelta]]

    # EventPayload fields (flattened)
    type: Series[
        str
    ]  # Enum type not directly supported with pandera, but pydantic will validate this later on.
    values: Series[pa.Object]  # Type validation will be done by pydantic later.

    class Config:
        strict = "filter"  # Filter out any columns not specified in the schema here.

    @pa.check("values")
    def payload_values_atleast_one(cls, values: Series) -> Series[bool]:
        return values.map(lambda v: isinstance(v, list) and len(v) > 0)  # type: ignore


class DataFrameEventIntervalConverter(
    BaseEventIntervalConverter[pd.DataFrame, dict[Hashable, Any]]
):
    def validate_input(self, input: pd.DataFrame) -> ValidationOutput:
        try:
            _ = _EventIntervalDataFrameSchema.validate(input)
            return OK()
        except Exception as e:
            return ERROR(exception=ExceptionGroup("Validation errors occured", [e]))

    def has_interval_period(self, row: dict[Hashable, Any]) -> bool:
        return row.get("start") is not None

    def to_iterable(self, input):
        return input.to_dict(orient="records")
