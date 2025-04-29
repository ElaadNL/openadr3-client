"""Module containing the conversion logic for Pandas dataframes."""

from collections.abc import Hashable, Iterable
from typing import Any

import pandas as pd
import pandera as pa
from pandera.engines.pandas_engine import DateTime
from pandera.typing import Series, Timedelta

from openadr3_client.conversion._base_converter import (
    ERROR,
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)


class _EventIntervalDataFrameSchema(pa.DataFrameModel):
    # IntervalPeriod fields (flattened)
    # time_zone_agnostic datetime available as of https://github.com/unionai-oss/pandera/pull/1902
    start: Series[DateTime(time_zone_agnostic=True)] | None  # type: ignore[reportInvalidTypeForm, valid-type]
    duration: Series[Timedelta] | None
    randomize_start: Series[Timedelta] | None

    # EventPayload fields (flattened)
    type: Series[str]  # Enum type not directly supported with pandera, but pydantic will validate this later on.
    values: Series[pa.Object]  # Type validation will be done by pydantic later.

    class Config:
        strict = "filter"  # Filter out any columns not specified in the schema here.

    @pa.check("values")
    def payload_values_atleast_one(self, values: Series) -> Series[bool]:
        return values.map(lambda v: isinstance(v, list) and len(v) > 0)  # type: ignore[return-value]


class DataFrameEventIntervalConverter(BaseEventIntervalConverter[pd.DataFrame, dict[Hashable, Any]]):
    """Class responsible for converting pandas dataframes to event interval(s)."""

    def validate_input(self, df_input: pd.DataFrame) -> ValidationOutput:
        """
        Validates the pandas dataframe to be compatible with event interval conversion.

        Validation is done by validating the da taframe against a pandera schema.

        Args:
            df_input (pd.DataFrame): The dataframe to validate.

        Returns:
            ValidationOutput: The output of the validation.

        """
        try:
            _ = _EventIntervalDataFrameSchema.validate(df_input)
            return OK()
        except Exception as e:  # noqa: BLE001
            return ERROR(exception=ExceptionGroup("Validation errors occured", [e]))

    def has_interval_period(self, row: dict[Hashable, Any]) -> bool:
        """
        Determines whether the row has an interval period.

        Args:
            row (dict[Hashable, Any]): The row to check for an interval period.

        Returns:
            bool: Whether the row has an interval period.

        """
        return row.get("start") is not None

    def to_iterable(self, df_input: pd.DataFrame) -> Iterable[dict[Hashable, Any]]:
        """
        Converts the dataframe to an iterable.

        Args:
            df_input (pd.DataFrame): The dataframe to convert.

        Returns: An iterable of the dataframe, in records orientation.

        """
        return df_input.to_dict(orient="records")
