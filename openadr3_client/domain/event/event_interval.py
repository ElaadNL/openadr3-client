from typing import Optional, Tuple
from pydantic import field_validator

from openadr3_client.domain.common.interval_period import IntervalPeriod
from openadr3_client.domain.event.event_payload import EventPayload
from openadr3_client.domain.base_model import BaseModel


class EventInterval(BaseModel):
    id: int
    interval_period: Optional[IntervalPeriod] = None
    payloads: Tuple[EventPayload, ...]

    @field_validator("payloads", mode="after")
    @classmethod
    def payload_atleast_one(
        cls, payloads: Tuple[EventPayload, ...]
    ) -> Tuple[EventPayload, ...]:
        if len(payloads) == 0:
            raise ValueError(
                "Event interval payload must contain at least one payload."
            )
        return payloads
