"""Module containing the conversion logic for Pandas dataframes."""

from collections.abc import Hashable, Iterable
from typing import Any, final

import numpy as np
import pandas as pd

from openadr3_client.conversion.common.dataframe import EventIntervalDataFrameSchema
from openadr3_client.conversion.input.events._base_converter import (
    ERROR,
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)


@final
class PandasEventIntervalConverter(BaseEventIntervalConverter[pd.DataFrame, dict[Hashable, Any]]):
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

    def to_iterable(self, df_input: pd.DataFrame) -> Iterable[dict[Hashable, Any]]:
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
