"""Implements the abstract base class for the reports VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client._vtn.interfaces.filters import PaginationFilter
from openadr3_client.models.report.report import ExistingReport, NewReport


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
            target (TargetFilter): The target to filter on.
            pagination (PaginationFilter): The pagination to apply.
            program_id (str): The program id to filter on.
            event_id (str): The event id to filter on.
            client_name (str): The client name to filter on.

        """

    @abstractmethod
    def get_report_by_id(self, report_id: str) -> ExistingReport:
        """
        Retrieves a report by the report identifier.

        Raises an error if the report could not be found.

        Args:
            report_id (str): The report identifier to retrieve.

        """


class WriteOnlyReportsInterface(ABC):
    """Abstract class which contains the interface for write only methods of reports."""

    @abstractmethod
    def create_report(self, new_report: NewReport) -> ExistingReport:
        """
        Creates a report from the new report.

        Returns the created report response from the VTN as an ExistingReport.

        Args:
            new_report (NewReport): The new report to create.

        """

    @abstractmethod
    def update_report_by_id(self, report_id: str, updated_report: ExistingReport) -> ExistingReport:
        """
        Update the report with the report identifier in the VTN.

        If the report id does not match the id in the existing report, an error is
        raised.

        Returns the updated report response from the VTN.

        Args:
            report_id (str): The identifier of the report to update.
            updated_report (ExistingReport): The updated report.

        """

    @abstractmethod
    def delete_report_by_id(self, report_id: str) -> None:
        """
        Delete the report with the identifier in the VTN.

        Args:
            report_id (str): The identifier of the report to delete.

        """


class ReadWriteReportsInterface(ReadOnlyReportsInterface, WriteOnlyReportsInterface):
    """Class which allows both read and write access on the resource."""
