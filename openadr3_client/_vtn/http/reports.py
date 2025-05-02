"""Implements the communication with the reports interface of an OpenADR 3 VTN."""

from pydantic.type_adapter import TypeAdapter

from openadr3_client._vtn.http.common._authenticated_session import bearer_authenticated_session
from openadr3_client._vtn.http.http_interface import HttpInterface
from openadr3_client._vtn.interfaces.filters import PaginationFilter
from openadr3_client._vtn.interfaces.reports import (
    ReadOnlyReportsInterface,
    ReadWriteReportsInterface,
    WriteOnlyReportsInterface,
)
from openadr3_client.logging import logger
from openadr3_client.models.report.report import ExistingReport, NewReport

base_prefix = "reports"


class ReportsReadOnlyHttpInterface(ReadOnlyReportsInterface, HttpInterface):
    """Implements the read communication with the reports HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

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
        # Convert the filters to dictionaries and union them. No key clashing can happen, as the properties
        # of the filters are unique.
        query_params: dict = {}

        if pagination:
            query_params |= pagination.model_dump(by_alias=True, mode="json")

        if program_id:
            query_params |= {"programID": program_id}

        if client_name:
            query_params |= {"clientName": client_name}

        if event_id:
            query_params |= {"eventID": event_id}

        logger.debug("Reports - Performing get_reports request with query params: %s", query_params)

        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingReport])
        return tuple(adapter.validate_python(response.json()))

    def get_report_by_id(self, report_id: str) -> ExistingReport:
        """
        Retrieves a report by the report identifier.

        Raises an error if the report could not be found.

        Args:
            report_id (str): The report identifier to retrieve.

        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{report_id}")
        response.raise_for_status()

        return ExistingReport.model_validate(response.json())


class ReportsWriteOnlyHttpInterface(WriteOnlyReportsInterface, HttpInterface):
    """Implements the write communication with the reports HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def create_report(self, new_report: NewReport) -> ExistingReport:
        """
        Creates a report from the new report.

        Returns the created report response from the VTN as an ExistingReport.

        Args:
            new_report (NewReport): The new report to create.

        """
        with new_report.with_creation_guard():
            response = bearer_authenticated_session.post(
                f"{self.base_url}/{base_prefix}", json=new_report.model_dump(by_alias=True, mode="json")
            )
            response.raise_for_status()
            return ExistingReport.model_validate(response.json())

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
        if report_id != updated_report.id:
            exc_msg = "Report id does not match report id of updated report object."
            raise ValueError(exc_msg)

        # No lock on the ExistingReport type exists similar to the creation guard of a NewReport.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(
            f"{self.base_url}/{base_prefix}/{report_id}", json=updated_report.model_dump(by_alias=True, mode="json")
        )
        response.raise_for_status()
        return ExistingReport.model_validate(response.json())

    def delete_report_by_id(self, report_id: str) -> None:
        """
        Delete the report with the identifier in the VTN.

        Args:
            report_id (str): The identifier of the report to delete.

        """
        response = bearer_authenticated_session.delete(f"{self.base_url}/{base_prefix}/{report_id}")
        response.raise_for_status()


class ReportsHttpInterface(ReadWriteReportsInterface, ReportsReadOnlyHttpInterface, ReportsWriteOnlyHttpInterface):
    """Implements the read and write communication with the reports HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
