"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from contextlib import contextmanager
from threading import Lock
from typing import TYPE_CHECKING, final

from pydantic import AwareDatetime, Field, PrivateAttr, field_validator

from openadr3_client.models._base_model import BaseModel
from openadr3_client.models.common.interval import Interval
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.event.event_payload import EventPayloadDescriptor
from openadr3_client.models.model import ValidatableModel
from openadr3_client.models.report.report_payload import ReportPayload

if TYPE_CHECKING:
    from collections.abc import Iterator


@final
class ReportResource(ValidatableModel):
    """Class representing a resource of a report."""

    resource_name: str = Field(min_length=1, max_length=128)
    """Resource name of the resource this report interval is related to."""

    interval_period: IntervalPeriod | None = None
    """The interval period of the resource."""

    intervals: tuple[Interval[ReportPayload], ...]
    """The intervals of the report."""

    @field_validator("intervals", mode="after")
    @classmethod
    def atleast_one_interval(
        cls, intervals: tuple[Interval[ReportPayload], ...]
    ) -> tuple[Interval[ReportPayload], ...]:
        """
        Validatest that a resource has atleast one interval defined.

        Args:
            intervals (tuple[Interval[ReportPayload], ...]): The intervals of the resource.

        """
        if len(intervals) == 0:
            err_msg = "ReportResource must contain at least one interval."
            raise ValueError(err_msg)
        return intervals


class Report[T](ABC, ValidatableModel):
    """Base class for reports."""

    id: T
    """The identifier for the report."""

    program_id: str = Field(alias="programID", min_length=1, max_length=128)
    """The program this report is related to."""

    event_id: str = Field(alias="eventID", min_length=1, max_length=128)
    """The event this report is related to."""

    client_name: str = Field(min_length=1, max_length=128)
    """The name of the client this report is related to."""

    report_name: str | None = None
    """The optional name of the report for use in debugging or UI display."""

    payload_descriptor: tuple[EventPayloadDescriptor, ...] | None = None
    """The payload descriptors of the report."""

    resources: tuple[ReportResource, ...]
    """The resources of the report."""


@final
class NewReport(Report[None]):
    """Class representing a new report not yet pushed to the VTN."""

    """Private flag to track if Report has been used to create a report in the VTN.

    If this flag is set to true, calls to create a report inside the VTN with
    this NewReport object will be rejected."""
    _created: bool = PrivateAttr(default=False)

    """Lock object to synchronize access to with_creation_guard."""
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @contextmanager
    def with_creation_guard(self) -> Iterator[None]:
        """
        A guard which enforces that a NewReport can only be used once.

        A NewReport can only be used to create a report inside a VTN exactly once.
        Subsequent calls to create the NewReport with the same object will raise an
        exception.

        Raises:
            ValueError: Raised if the NewReport has already been created inside the VTN.

        """
        with self._lock:
            if self._created:
                err_msg = "NewReport has already been created."
                raise ValueError(err_msg)

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise

    @field_validator("resources", mode="after")
    @classmethod
    def atleast_one_resource(cls, resources: tuple[ReportResource, ...]) -> tuple[ReportResource, ...]:
        """
        Validatest that a report has atleast one resource defined.

        Args:
            resources (tuple[ReportResource, ...]): The resources of the report.

        """
        if len(resources) == 0:
            err_msg = "NewReport must contain at least one resource."
            raise ValueError(err_msg)
        return resources


@final
class ReportUpdate(BaseModel):
    """Class representing an update to a report."""

    program_id: str | None = Field(alias="programID", default=None, min_length=1, max_length=128)
    """The program this report is related to."""

    event_id: str | None = Field(alias="eventID", default=None, min_length=1, max_length=128)
    """The event this report is related to."""

    client_name: str | None = Field(min_length=1, max_length=128)
    """The name of the client this report is related to."""

    report_name: str | None = None
    """The optional name of the report for use in debugging or UI display."""

    payload_descriptor: tuple[EventPayloadDescriptor, ...] | None = None
    """The payload descriptors of the report."""

    resources: tuple[ReportResource, ...] | None = None
    """The resources of the report."""


@final
class ExistingReport(Report[str]):
    """Class representing an existing report retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    def update(self, update: ReportUpdate) -> ExistingReport:
        """
        Update the existing report with the provided update.

        Args:
            update (ReportUpdate): The update to apply to the report.

        Returns:
            ExistingReport: The updated report.

        """
        current_report = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_report = current_report | update_dict
        return ExistingReport(**updated_report)
