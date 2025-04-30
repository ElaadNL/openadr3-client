"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from contextlib import contextmanager
from threading import Lock
from typing import TYPE_CHECKING, final

from pydantic import AwareDatetime, Field, NonNegativeInt, PrivateAttr, field_validator

from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.common.target import Target
from openadr3_client.models.event.event_payload import EventPayload, EventPayloadDescriptor
from openadr3_client.models.model import ValidatableModel
from openadr3_client.models._base_model import BaseModel

if TYPE_CHECKING:
    from collections.abc import Iterator


class Event[T](ABC, ValidatableModel):
    """Base class for events."""

    id: T
    """The identifier for the event."""

    program_id: str = Field(alias="programID", min_length=1, max_length=128)
    """Identifier of the program this event belongs to."""

    event_name: str | None = None
    """The name of the event."""

    priority: NonNegativeInt | None = None
    """The priority of the event, less is higher priority."""

    targets: tuple[Target, ...] | None = None
    """The targets of the event."""

    payload_descriptor: tuple[EventPayloadDescriptor, ...] | None = None
    """The payload descriptors of the event."""

    interval_period: IntervalPeriod | None = None
    """The interval period of the event."""

    intervals: tuple[Interval[EventPayload], ...]
    """The intervals of the event."""


class EventUpdate(BaseModel):
    """Class representing an update to an existing event."""

    program_id: str | None = Field(alias="programID", min_length=1, max_length=128, default=None)
    """Identifier of the program this event belongs to."""

    event_name: str | None = None
    """The name of the event."""

    priority: NonNegativeInt | None = None
    """The priority of the event, less is higher priority."""

    targets: tuple[Target, ...] | None = None
    """The targets of the event."""

    payload_descriptor: tuple[EventPayloadDescriptor, ...] | None = None
    """The payload descriptors of the event."""

    interval_period: IntervalPeriod | None = None
    """The interval period of the event."""

    intervals: tuple[Interval[EventPayload], ...] | None = None
    """The intervals of the event."""


@final
class NewEvent(Event[None]):
    """Class representing a new event not yet pushed to the VTN."""

    _created: bool = PrivateAttr(default=False)
    """Private flag to track if NewEvent has been used to create an event in the VTN.

    If this flag is set to true, calls to create an event inside the VTN with
    this NewEvent object will be rejected."""

    _lock: Lock = PrivateAttr(default_factory=Lock)
    """Lock object to synchronize access to with_creation_guard."""

    @contextmanager
    def with_creation_guard(self) -> Iterator[None]:
        """
        A guard which enforces that a NewEvent can only be used once.

        A NewEvent can only be used to create an event inside a VTN exactly once.
        Subsequent calls to create the event with the same object will raise an
        exception.

        Raises:
            ValueError: Raised if the NewEvent has already been created inside the VTN.

        """
        with self._lock:
            if self._created:
                err_msg = "NewEvent has already been created."
                raise ValueError(err_msg)

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise

    @field_validator("intervals", mode="after")
    @classmethod
    def atleast_one_interval(cls, intervals: tuple[Interval, ...]) -> tuple[Interval, ...]:
        """
        Validatest that an event has atleast one interval defined.

        Args:
            intervals (tuple[Interval, ...]): The intervals of the event.

        """
        if len(intervals) == 0:
            err_msg = "NewEvent must contain at least one interval."
            raise ValueError(err_msg)
        return intervals


@final
class ExistingEvent(Event[str]):
    """Class representing an existing event retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    def update(self, update: EventUpdate) -> "ExistingEvent":
        """
        Update this event with the provided update.

        Args:
            update: The update to apply to this event.

        Returns:
            A new ExistingEvent instance with the updates applied.
        """
        current_data = self.model_dump()
        update_data = update.model_dump(exclude_unset=True)
        updated_data = {**current_data, **update_data}
        return ExistingEvent(**updated_data)
