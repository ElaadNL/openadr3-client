from collections.abc import Iterable
from typing import final

from openadr3_client.conversion.common.dict import EventIntervalDictInput
from openadr3_client.conversion.output._base_converter import BaseOutputConverter
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.event.event_payload import EventPayload


@final
class DictEventIntervalConverter(BaseOutputConverter[list[Interval[EventPayload]], Iterable[EventIntervalDictInput]]):
    """Class which can convert a list of event intervals to a list of EventIntervalDictInput."""

    def convert(self, given_input: list[Interval[EventPayload]]) -> Iterable[EventIntervalDictInput]:
        """
        Convert the event intervals to a list of EventIntervalDictInput.

        Args:
            given_input (list[Interval[EventPayload]]): The event intervals to convert.

        Returns: The converted event intervals.

        """
        return [self._to_event_interval_dict_input(interval) for interval in given_input]

    def _to_event_interval_dict_input(self, interval: Interval[EventPayload]) -> EventIntervalDictInput:
        """
        Convert the event interval to an EventIntervalDictInput.

        Args:
            interval (Interval[EventPayload]): The event interval to convert.

        Returns: The converted event interval.

        """
        return {
            # For now, a constraint of the implementation is that there is only a single payload per interval.
            "type": interval.payloads[0].type.value,
            "values": list(interval.payloads[0].values),
            "start": interval.interval_period.start if interval.interval_period else None,
            "duration": interval.interval_period.duration if interval.interval_period else None,
            "randomize_start": interval.interval_period.randomize_start if interval.interval_period else None,
        }
