"""Module containing the conversion logic for Pandas dataframes."""

from collections.abc import Hashable, Iterable
from typing import Any, final

from openadr3_client.oadr310.models.common.interval import Interval
from openadr3_client.oadr310.models.common.interval_period import IntervalPeriod
from openadr3_client.oadr310.models.event.event_payload import EventPayload

try:
    import numpy as np
    import pandas as pd
except ImportError as e:
    msg = "DataFrame conversion functionality requires the 'pandas' extra. Install it with: pip install 'openadr3-client[pandas]' or the equivalent in your package manager."
    raise ImportError(msg) from e

from openadr3_client._conversion.common.dataframe import EventIntervalDataFrameSchema
from openadr3_client._conversion.input._base_converter import (
    ERROR,
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)


@final
class PandasEventIntervalConverter(BaseEventIntervalConverter[dict[Hashable, Any], pd.DataFrame, Interval[EventPayload]]):
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
            _ = EventIntervalDataFrameSchema.validate(df_input)
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

    def _do_convert(self, row_id: int, row: dict[Hashable, Any]) -> Interval[EventPayload]:
        interval_period = IntervalPeriod.model_validate(row) if self.has_interval_period(row) else None
        # For now, we are assuming that there will only be a single payload per interval.
        # We could support multiple, but we dont need to for the GAC spec.
        # So this would be a nice improvement further down the line.
        payload: EventPayload = EventPayload.model_validate(row)
        return Interval(id=row_id, interval_period=interval_period, payloads=(payload,))

    def _to_iterable(self, df_input: pd.DataFrame) -> Iterable[dict[Hashable, Any]]:
        """
        Converts the dataframe to an iterable.

        Args:
            df_input (pd.DataFrame): The dataframe to convert.

        Returns: An iterable of the dataframe, in records orientation.

        """
        # Convert any columns that are potential pandas types (NaT) to 'normal' types (None).
        df_pre_processed = df_input.copy(deep=True)
        # Replace NaNs / NaTs with None.
        df_pre_processed = df_pre_processed.replace({np.nan: None})
        return df_pre_processed.to_dict(orient="records")
