from datetime import datetime, timedelta
from typing import Iterable, Optional, TypedDict

from openadr3_client.input_conversion._base_converter import (
    OK,
    BaseEventIntervalConverter,
    ValidationOutput,
)
from openadr3_client.domain.event.event_payload import AllowedPayloadInputs


class _EventIntervalDictRequiredFields(TypedDict):
    """Required dictionary keys for event interval dict.

    Seperated from the optional parameters, as Optional[X] still requires the key to be present
    in the dictionary. While we want them to be ommittable.
    """

    # EventPayload fields (flattened)
    type: str
    values: list[AllowedPayloadInputs]


class EventIntervalDictInput(_EventIntervalDictRequiredFields, total=False):
    """TypedDict for the event interval input.

    Inherits the required fields which are required inside the dictionary, all the keys
    defined here are optional.
    """

    # IntervalPeriod fields (flattened)
    start: Optional[datetime]
    duration: Optional[timedelta]
    randomize_start: Optional[timedelta]


class IterableEventIntervalConverter(
    BaseEventIntervalConverter[Iterable[EventIntervalDictInput], EventIntervalDictInput]
):
    def validate_input(self, row) -> ValidationOutput:
        # Validation is handled by pydantic, there is no pre-validation step
        # which we can execute here.
        return OK()

    def has_interval_period(self, row: EventIntervalDictInput) -> bool:
        return row.get("start") is not None

    def to_iterable(self, input):
        return input
