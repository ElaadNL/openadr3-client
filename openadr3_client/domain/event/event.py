"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from contextlib import contextmanager
from threading import Lock
from typing import TYPE_CHECKING

from pydantic import AwareDatetime, Field, PrivateAttr, field_validator

from openadr3_client.domain.common.interval_period import IntervalPeriod
from openadr3_client.domain.common.target import Target
from openadr3_client.domain.event.event_interval import EventInterval
from openadr3_client.domain.event.event_payload import EventPayloadDescriptor
from openadr3_client.domain.model import ValidatableModel

if TYPE_CHECKING:
    from collections.abc import Iterator


class Event[T](ABC, ValidatableModel):
    """Base class for events."""

    """The identifier for the event."""
    id: T

    """Identifier of the program this event belongs to."""
    program_id: str = Field(alias="programID")

    """The name of the event."""
    event_name: str | None = None

    """The priority of the event, less is higher priority."""
    priority: int | None = None

    """The targets of the event."""
    targets: tuple[Target, ...] | None = None

    """The payload descriptors of the event."""
    payload_descriptor: tuple[EventPayloadDescriptor, ...] | None = None

    """The interval period of the event."""
    interval_period: IntervalPeriod | None = None

    """The intervals of the event."""
    intervals: tuple[EventInterval, ...]


class NewEvent(Event[None]):
    """Class representing a new event not yet pushed to the VTN."""

    """Private flag to track if NewEvent has been used to create an event in the VTN.

    If this flag is set to true, calls to create an event inside the VTN with
    this NewEvent object will be rejected."""
    _created: bool = PrivateAttr(default=False)

    """Lock object to synchronize access to with_creation_guard."""
    _lock: Lock = PrivateAttr(default_factory=Lock)

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
    def atleast_one_interval(cls, intervals: tuple[EventInterval, ...]) -> tuple[EventInterval, ...]:
        """
        Validatest that an event has atleast one interval defined.

        Args:
            intervals (tuple[EventInterval, ...]): The intervals of the event.

        """
        if len(intervals) == 0:
            err_msg = "NewEvent must contain at least one event interval."
            raise ValueError(err_msg)
        return intervals


class ExistingEvent(Event[str]):
    """Class representing an existing event retrieved from the VTN."""

    created_datetime: AwareDatetime
    modification_datetime: AwareDatetime
