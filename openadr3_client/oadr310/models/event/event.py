# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from datetime import timedelta  # noqa: TC003
from typing import final

from pydantic import AwareDatetime, Field, NonNegativeInt

from openadr3_client._models._base_model import BaseModel
from openadr3_client._models._validatable_model import OpenADRResource
from openadr3_client._models.common.creation_guarded import CreationGuarded
from openadr3_client._models.common.interval import Interval
from openadr3_client._models.common.interval_period import IntervalPeriod
from openadr3_client.oadr310.models.event.event_payload import EventPayload, EventPayloadDescriptor
from openadr3_client.oadr310.models.report.report_payload import ReportDescriptor


class _EventBase(BaseModel):
    """Base class containing common properties for Event and EventUpdate."""

    program_id: str = Field(alias="programID", min_length=1, max_length=128)
    """Identifier of the program this event belongs to."""

    event_name: str | None = None
    """The name of the event."""

    priority: NonNegativeInt | None = None
    """The priority of the event, less is higher priority."""

    targets: tuple[str, ...] | None = None
    """The targets of the event."""

    payload_descriptors: tuple[EventPayloadDescriptor, ...] | None = None
    """The payload descriptors of the event."""

    report_descriptors: tuple[ReportDescriptor, ...] | None = None
    """The report descriptors of the event."""

    interval_period: IntervalPeriod | None = None
    """The interval period of the event."""

    intervals: tuple[Interval[EventPayload], ...] | None = None
    """The intervals of the event."""

    duration: timedelta | None = None
    """The duration of the event.

    The event property 'duration' may be used to augment intervalPeriod definitions to shorten or lengthen the temporal span of an event.
    For example, event.duration = "P9999Y" indicates the set of intervals repeat indefinitely.

    For additional information related to the usage of this field
    consult the OpenADR 3.1.0 user guide."""


class Event(ABC, OpenADRResource, _EventBase):
    """Base class for events."""

    @property
    def name(self) -> str | None:
        """Helper method to get the name field of the model."""
        return self.event_name


@final
class EventUpdate(_EventBase):
    """Class representing an update to an existing event."""


@final
class NewEvent(Event, CreationGuarded):
    """Class representing a new event not yet pushed to the VTN."""


class ServerEvent(Event):
    """Class representing an event retrieved from the VTN."""

    id: str
    """The identifier for the event."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime


@final
class ExistingEvent(ServerEvent):
    """Class representing an existing event retrieved from the VTN."""

    def update(self, update: EventUpdate) -> ExistingEvent:
        """
        Update this event with the provided update.

        Args:
            update: The update to apply to this event.

        Returns:
            A new ExistingEvent instance with the updates applied.

        """
        current_data = self.model_dump()
        update_data = update.model_dump(exclude_unset=True)
        updated_data = current_data | update_data
        return ExistingEvent(**updated_data)


@final
class DeletedEvent(ServerEvent):
    """Class representing a deleted event."""
