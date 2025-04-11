"""Module containing the base model for the input converter of the openadr3 client."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List
from openadr3_client.domain.event.event_interval import EventInterval, IntervalPeriod

from openadr3_client.domain.event.event_payload import EventPayload


@dataclass
class OK:
    pass  # No fields for the validation


@dataclass
class ERROR:
    exception: ExceptionGroup


ValidationOutput = OK | ERROR


class BaseEventIntervalConverter[INPUTTYPE, ROWTYPE](ABC):  # type: ignore
    @abstractmethod
    def to_iterable(self, input: INPUTTYPE) -> Iterable[ROWTYPE]: ...

    @abstractmethod
    def has_interval_period(self, row: ROWTYPE) -> bool: ...

    @abstractmethod
    def validate_input(self, input: INPUTTYPE) -> ValidationOutput: ...

    def _do_convert(self, id: int, row: ROWTYPE) -> EventInterval:
        interval_period = (
            IntervalPeriod.model_validate(row)
            if self.has_interval_period(row)
            else None
        )
        # For now, we are assuming that there will only be a single payload per interval.
        # We could support multiple, but we dont need to for the GAC spec.
        # So this would be a nice improvement further down the line.
        payload: EventPayload = EventPayload.model_validate(row)
        return EventInterval(id=id, interval_period=interval_period, payloads=(payload,))

    def convert(self, input: INPUTTYPE) -> List[EventInterval]:
        """Convert the input to a list of event intervals"""
        intervals: List[EventInterval] = []
        errors = []

        validation_result = self.validate_input(input)

        match validation_result:
            case ERROR(exception=e):
                raise e
            case OK():
                for i, row in enumerate(self.to_iterable(input)):
                    try:
                        intervals.append(self._do_convert(i, row))
                    except Exception as e:
                        errors.append(e)

                if errors:
                    raise ExceptionGroup(
                        "Conversion validation errors occurred", errors
                    )

        return intervals
