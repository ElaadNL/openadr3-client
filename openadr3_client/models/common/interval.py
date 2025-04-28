from pydantic import field_validator

from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.common.payload import _BasePayload
from openadr3_client.models.model import ValidatableModel


class Interval[PAYLOAD: _BasePayload](ValidatableModel):
    """
    Represents an interval within OpenADR 3.

    Intervals can have differing allowed payloads based on the OpenADR 3 resource the interval is assigned to.

    Args:
        ValidatableModel (ValidatableModel): The base class for pydantic models of the library.

    """

    id: int
    interval_period: IntervalPeriod | None = None
    payloads: tuple[PAYLOAD, ...]

    @field_validator("payloads", mode="after")
    @classmethod
    def payload_atleast_one(cls, payloads: tuple[PAYLOAD, ...]) -> tuple[PAYLOAD, ...]:
        """
        Validates that an interval has one or more payloads.

        Args:
            payloads (tuple[EventPayload, ...]): The payloads of the interval.

        Raises:
            ValueError: Raised if the interval does not have one or more payloads.

        """
        if len(payloads) == 0:
            err_msg = "interval payload must contain at least one payload."
            raise ValueError(err_msg)
        return payloads
