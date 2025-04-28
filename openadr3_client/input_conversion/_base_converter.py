"""Module containing the base model for the input converter of the openadr3 client."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass

from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.event.event_payload import EventPayload


@dataclass
class OK:
    pass  # No fields for the validation


@dataclass
class ERROR:
    exception: ExceptionGroup


ValidationOutput = OK | ERROR


class BaseEventIntervalConverter[INPUTTYPE, ROWTYPE](ABC):
    @abstractmethod
    def to_iterable(self, given_input: INPUTTYPE) -> Iterable[ROWTYPE]: ...

    @abstractmethod
    def has_interval_period(self, row: ROWTYPE) -> bool: ...

    @abstractmethod
    def validate_input(self, given_input: INPUTTYPE) -> ValidationOutput: ...

    def _do_convert(self, interval_id: int, row: ROWTYPE) -> Interval[EventPayload]:
        interval_period = IntervalPeriod.model_validate(row) if self.has_interval_period(row) else None
        # For now, we are assuming that there will only be a single payload per interval.
        # We could support multiple, but we dont need to for the GAC spec.
        # So this would be a nice improvement further down the line.
        payload: EventPayload = EventPayload.model_validate(row)
        return Interval(id=interval_id, interval_period=interval_period, payloads=(payload,))

    def convert(self, given_input: INPUTTYPE) -> list[Interval[EventPayload]]:
        """Convert the input to a list of event intervals."""
        intervals: list[Interval[EventPayload]] = []
        errors = []

        validation_result = self.validate_input(given_input)

        match validation_result:
            case ERROR(exception=e):
                raise e
            case OK():
                for i, row in enumerate(self.to_iterable(given_input)):
                    try:
                        intervals.append(self._do_convert(i, row))
                    except Exception as e:  # noqa: BLE001
                        errors.append(e)

                if errors:
                    err_msg = "Conversion validation errors occurred"
                    raise ExceptionGroup(err_msg, errors)

        return intervals
