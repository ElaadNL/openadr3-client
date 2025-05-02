from collections.abc import Iterable
from typing import final

from openadr3_client.conversion.common.dict import EventIntervalDictInput
from openadr3_client.conversion.input.events._base_converter import (
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)


@final
class DictEventIntervalConverter(BaseEventIntervalConverter[Iterable[EventIntervalDictInput], EventIntervalDictInput]):
    """Class responsible for converting iterables of dictionaries to event interval(s)."""

    def validate_input(self, _: Iterable[EventIntervalDictInput]) -> ValidationOutput:
        """
        Validates the input to be compatible with event interval conversion.

        Args:
            dict_input (Iterable[EventIntervalDictInput]): The input to validate.

        Returns:
            ValidationOutput: The output of the validation.

        """
        # Validation is handled by pydantic, there is no pre-validation step
        # which we can execute here.
        return OK()

    def has_interval_period(self, row: EventIntervalDictInput) -> bool:
        """
        Determines whether the row has an interval period.

        Args:
            row (EventIntervalDictInput): The row to check for an interval period.

        Returns:
            bool: Whether the row has an interval period.

        """
        return row.get("start") is not None

    def to_iterable(self, dict_input: Iterable[EventIntervalDictInput]) -> Iterable[EventIntervalDictInput]:
        """
        Implemented to satisfy the contract of converting arbitrary inputs to an interable.

        Simply returns the input parameter, as it is already an interable.

        Args:
            dict_input (Iterable[EventIntervalDictInput]): The iterable to convert.

        Returns: The input value.

        """
        return dict_input
