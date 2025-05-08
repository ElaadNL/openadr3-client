from collections.abc import Iterable
from typing import final

from pydantic import ValidationError

from openadr3_client.conversion.common.dict import EventIntervalDictInput, EventIntervalDictPydanticValidator
from openadr3_client.conversion.input.events._base_converter import (
    ERROR,
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)


@final
class DictEventIntervalConverter(BaseEventIntervalConverter[Iterable[EventIntervalDictInput], EventIntervalDictInput]):
    """Class responsible for converting iterables of dictionaries to event interval(s)."""

    def validate_input(self, event_interval_dict_input: Iterable[EventIntervalDictInput]) -> ValidationOutput:
        """
        Validates the input to be compatible with event interval conversion.

        Args:
            event_interval_dict_input (Iterable[EventIntervalDictInput]): The input to validate.

        Returns:
            ValidationOutput: The output of the validation.

        """
        # Pass the input through a pydantic validator to ensure the input is valid
        # even if the user does not have a type checker enabled.
        validation_errors = []
        for dict_input in event_interval_dict_input:
            try:
                _ = EventIntervalDictPydanticValidator.model_validate(dict_input)
            except ValidationError as e:
                validation_errors.append(e)

        if validation_errors:
            return ERROR(exception=ExceptionGroup("Dict input validation errors occured", validation_errors))

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
