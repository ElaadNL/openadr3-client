"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from typing import final

from pydantic import AwareDatetime, Field, field_validator

from openadr3_client._models._base_model import BaseModel
from openadr3_client._models._validatable_model import OpenADRResource, ValidatableModel
from openadr3_client.oadr310.models.common.creation_guarded import CreationGuarded
from openadr3_client.oadr310.models.common.interval import Interval
from openadr3_client.oadr310.models.common.interval_period import IntervalPeriod
from openadr3_client.oadr310.models.event.event_payload import EventPayloadDescriptor
from openadr3_client.oadr310.models.report.report_payload import ReportPayload


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
    def atleast_one_interval(cls, intervals: tuple[Interval[ReportPayload], ...]) -> tuple[Interval[ReportPayload], ...]:
        """
        Validatest that a resource has atleast one interval defined.

        Args:
            intervals (tuple[Interval[ReportPayload], ...]): The intervals of the resource.

        """
        if len(intervals) == 0:
            err_msg = "ReportResource must contain at least one interval."
            raise ValueError(err_msg)
        return intervals


class _ReportBase(BaseModel):
    """Base class containing common properties for Report and ReportUpdate."""

    event_id: str = Field(alias="eventID", min_length=1, max_length=128)
    """The event this report is related to."""

    client_name: str = Field(min_length=1, max_length=128)
    """The name of the client this report is related to."""

    report_name: str | None = None
    """The optional name of the report for use in debugging or UI display."""

    payload_descriptors: tuple[EventPayloadDescriptor, ...] | None = None
    """The payload descriptors of the report."""

    resources: tuple[ReportResource, ...]
    """The resources of the report."""


class Report(ABC, OpenADRResource, _ReportBase):
    """Base class for reports."""

    @property
    def name(self) -> str | None:
        """Helper method to get the name field of the model."""
        return self.report_name


@final
class NewReport(Report, CreationGuarded):
    """Class representing a new report not yet pushed to the VTN."""

    @field_validator("resources", mode="after")
    @classmethod
    def atleast_one_resource(cls, resources: tuple[ReportResource, ...]) -> tuple[ReportResource, ...]:
        """
        Validates that a report has at least one resource defined.

        Args:
            resources (tuple[ReportResource, ...]): The resources of the report.

        """
        if len(resources) == 0:
            err_msg = "NewReport must contain at least one resource."
            raise ValueError(err_msg)
        return resources


@final
class ReportUpdate(_ReportBase):
    """Class representing an update to a report."""


class ServerReport(Report):
    """Class representing a report retrieved from the VTN."""

    id: str
    """The identifier for the report."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime


@final
class ExistingReport(ServerReport):
    """Class representing an existing report retrieved from the VTN."""

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


@final
class DeletedReport(ServerReport):
    """Class representing a deleted report."""
