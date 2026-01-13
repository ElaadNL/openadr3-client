# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Implements the abstract base class for the reports VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client.oadr310._vtn.interfaces.filters import PaginationFilter
from openadr3_client.oadr310.models.report.report import DeletedReport, ExistingReport, NewReport, ReportUpdate


class ReadOnlyReportsInterface(ABC):
    """Abstract class which contains the interface for read only methods of reports."""

    @abstractmethod
    def get_reports(
        self,
        pagination: PaginationFilter | None,
        program_id: str | None,
        event_id: str | None,
        client_name: str | None,
    ) -> tuple[ExistingReport, ...]:
        """
        Retrieve reports from the VTN.

        Args:
            target: The target to filter on.
            pagination: The pagination to apply.
            program_id: The program id to filter on.
            event_id: The event id to filter on.
            client_name: The client name to filter on.

        """

    @abstractmethod
    def get_report_by_id(self, report_id: str) -> ExistingReport:
        """
        Retrieves a report by the report identifier.

        Raises an error if the report could not be found.

        Args:
            report_id: The report identifier to retrieve.

        """


class WriteOnlyReportsInterface(ABC):
    """Abstract class which contains the interface for write only methods of reports."""

    @abstractmethod
    def create_report(self, new_report: NewReport) -> ExistingReport:
        """
        Creates a report from the new report.

        Returns the created report response from the VTN as an ExistingReport.

        Args:
            new_report: The new report to create.

        """

    @abstractmethod
    def update_report_by_id(self, report_id: str, updated_report: ReportUpdate) -> ExistingReport:
        """
        Update the report with the report identifier in the VTN.

        If the report id does not match the id in the existing report, an error is
        raised.

        Returns the updated report response from the VTN.

        Args:
            report_id: The identifier of the report to update.
            updated_report: The update to apply to the report.

        """

    @abstractmethod
    def delete_report_by_id(self, report_id: str) -> DeletedReport:
        """
        Delete the report with the identifier in the VTN.

        Args:
            report_id: The identifier of the report to delete.

        """


class ReadWriteReportsInterface(ReadOnlyReportsInterface, WriteOnlyReportsInterface):
    """Class which allows both read and write access on the resource."""
