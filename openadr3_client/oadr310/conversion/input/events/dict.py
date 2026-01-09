from collections.abc import Iterable
from typing import final

from pydantic import ValidationError

from openadr3_client._conversion.common.dict import EventIntervalDictInput, EventIntervalDictPydanticValidator
from openadr3_client._conversion.input._base_converter import (
    ERROR,
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)
from openadr3_client._models.common.interval import Interval
from openadr3_client._models.common.interval_period import IntervalPeriod
from openadr3_client._models.common.payload import AllowedPayloadInputs
from openadr3_client.oadr310.models.event.event_payload import EventPayload


@final
class DictEventIntervalConverter(
    BaseEventIntervalConverter[EventIntervalDictInput[AllowedPayloadInputs], Iterable[EventIntervalDictInput[AllowedPayloadInputs]], Interval[EventPayload]]
):
    """Class responsible for converting iterables of dictionaries to event interval(s)."""

    def validate_input(self, event_interval_dict_input: Iterable[EventIntervalDictInput[AllowedPayloadInputs]]) -> ValidationOutput:
        """
        Validates the input to be compatible with event interval conversion.

        Args:
            event_interval_dict_input: The input to validate.

        Returns:
            The output of the validation.

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

    def has_interval_period(self, row: EventIntervalDictInput[AllowedPayloadInputs]) -> bool:
        """
        Determines whether the row has an interval period.

        Args:
            row: The row to check for an interval period.

        Returns:
            Whether the row has an interval period.

        """
        return row.get("start") is not None

    def _to_iterable(self, event_interval_dict_input: Iterable[EventIntervalDictInput[AllowedPayloadInputs]]) -> Iterable[EventIntervalDictInput[AllowedPayloadInputs]]:
        return event_interval_dict_input

    def _do_convert(self, row_id: int, row: EventIntervalDictInput[AllowedPayloadInputs]) -> Interval[EventPayload]:
        interval_period = IntervalPeriod.model_validate(row) if self.has_interval_period(row) else None
        # For now, we are assuming that there will only be a single payload per interval.
        # We could support multiple, but we dont need to for the GAC spec.
        # So this would be a nice improvement further down the line.
        payload: EventPayload = EventPayload.model_validate(row)
        return Interval(id=row_id, interval_period=interval_period, payloads=(payload,))
