"""Contains the domain types related to events."""

from __future__ import annotations
from abc import ABC
from contextlib import contextmanager
from threading import Lock
from typing import Iterator, Optional, Tuple

from pydantic import AwareDatetime, Field, PrivateAttr, field_validator, model_validator

from openadr3_client.domain.common.interval_period import IntervalPeriod
from openadr3_client.domain.event.event_interval import EventInterval
from openadr3_client.domain.event.event_payload import EventPayloadDescriptor
from openadr3_client.domain.common.target import Target
from openadr3_client.domain.base_model import BaseModel


class Event[T](ABC, BaseModel):
    """Base class for events."""

    """The identifier for the event."""
    id: T

    """Identifier of the program this event belongs to."""
    program_id: str = Field(alias="programID")

    """The name of the event."""
    event_name: Optional[str] = None

    """The priority of the event, less is higher priority."""
    priority: Optional[int] = None

    """The targets of the event."""
    targets: Optional[Tuple[Target, ...]] = None

    """The payload descriptors of the event."""
    payload_descriptor: Optional[Tuple[EventPayloadDescriptor, ...]] = None

    """The interval period of the event."""
    interval_period: Optional[IntervalPeriod] = None

    """The intervals of the event."""
    intervals: Tuple[EventInterval, ...]

    @model_validator(mode="after")
    def validate_interval_period(self: Event) -> 'Event':
        interval_period = self.interval_period
        intervals = self.intervals or ()

        if interval_period is None:
            # interval period not set at top level of the event.
            # Ensure that all intervals have the interval_period defined, to comply with the GAC specification.
            undefined_intervals_period = [
                i for i in intervals if i.interval_period is None
            ]
            if undefined_intervals_period:
                raise ValueError(
                    "Either 'interval_period' must be set on the event once, or every interval must have its own 'interval_period'."
                )
        else:
            # interval period set at top level of the event.
            # Ensure that all intervals do not have the interval_period defined, to comply with the GAC specification.
            duplicate_interval_period = [
                i for i in intervals if i.interval_period is not None
            ]
            if duplicate_interval_period:
                raise ValueError(
                    "Either 'interval_period' must be set on the event once, or every interval must have its own 'interval_period'."
                )

        return self


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
        with self._lock:
            if self._created:
                raise ValueError("NewEvent has already been created.")

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise

    @field_validator("intervals", mode="after")
    @classmethod
    def atleast_one_interval(
        cls, intervals: Tuple[EventInterval, ...]
    ) -> Tuple[EventInterval, ...]:
        if len(intervals) == 0:
            raise ValueError("NewEvent must contain at least one event interval.")
        return intervals


class ExistingEvent(Event[str]):
    """Class representing an existing event retrieved from the VTN."""

    created_datetime: AwareDatetime
    modification_datetime: AwareDatetime
