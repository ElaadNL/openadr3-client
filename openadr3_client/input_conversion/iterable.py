from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import TypedDict

from openadr3_client.models.common.payload import AllowedPayloadInputs
from openadr3_client.input_conversion._base_converter import (
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)


class _EventIntervalDictRequiredFields(TypedDict):
    """
    Required dictionary keys for event interval dict.

    Seperated from the optional parameters, as Optional[X] still requires the key to be present
    in the dictionary. While we want them to be ommittable.
    """

    # EventPayload fields (flattened)
    type: str
    values: list[AllowedPayloadInputs]


class EventIntervalDictInput(_EventIntervalDictRequiredFields, total=False):
    """
    TypedDict for the event interval input.

    Inherits the required fields which are required inside the dictionary, all the keys
    defined here are optional.
    """

    # IntervalPeriod fields (flattened)
    start: datetime | None
    duration: timedelta | None
    randomize_start: timedelta | None


class IterableEventIntervalConverter(
    BaseEventIntervalConverter[Iterable[EventIntervalDictInput], EventIntervalDictInput]
):
    """Class responsible for converting iterables to event interval(s)."""

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
