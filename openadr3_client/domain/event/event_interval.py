from pydantic import field_validator

from openadr3_client.domain.common.interval_period import IntervalPeriod
from openadr3_client.domain.event.event_payload import EventPayload
from openadr3_client.domain.model import ValidatableModel


class EventInterval(ValidatableModel):
    """
    Represents an event interval of OpenADR 3.

    Args:
        ValidatableModel (ValidatableModel): The base class for pydantic models of the library.

    """

    id: int
    interval_period: IntervalPeriod | None = None
    payloads: tuple[EventPayload, ...]

    @field_validator("payloads", mode="after")
    @classmethod
    def payload_atleast_one(cls, payloads: tuple[EventPayload, ...]) -> tuple[EventPayload, ...]:
        """
        Validates that an event interval has one or more payloads.

        Args:
            payloads (tuple[EventPayload, ...]): The payloads of the event interval.

        Raises:
            ValueError: Raised if the event interval does not have one or more payloads.

        """
        if len(payloads) == 0:
            err_msg = "Event interval payload must contain at least one payload."
            raise ValueError(err_msg)
        return payloads
