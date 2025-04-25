"""Implements the communication with the reports interface of an OpenADR 3 VTN."""
from typing import List, Optional, Tuple

from pydantic.type_adapter import TypeAdapter
from openadr3_client.vtn.common.filters import PaginationFilter
from openadr3_client.domain.report.report import ExistingReport, NewReport
from openadr3_client.vtn.common._authenticated_session import bearer_authenticated_session

from dataclasses import asdict

base_prefix = "/reports"

class ReportsReadOnlyInterface:
    """Implements the read communication with the reports HTTP interface of an OpenADR 3 VTN."""

    def get_reports(self, pagination: Optional[PaginationFilter], program_id: Optional[str], event_id: Optional[str], client_name: Optional[str]) -> Tuple[ExistingReport, ...]:
        """Retrieve reports from the VTN.
        
        Args:
            target (TargetFilter): The target to filter on.
            pagination (PaginationFilter): The pagination to apply.
            program_id (str): The program id to filter on.
            event_id (str): The event id to filter on.
            client_name (str): The client name to filter on.
        """

        # Convert the filters to dictionaries and union them. No key clashing can happen, as the properties
        # of the filters are unique.
        query_params = \
            asdict(pagination) if pagination else {} \
            | {"programID": program_id} if program_id else {} \
            | {"eventID": event_id} if event_id else {} \
            | {"clientName": client_name} if client_name else {}

        response = bearer_authenticated_session.get(f"{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(List[ExistingReport])
        return tuple(adapter.validate_json(response.json()))

    def get_report_by_id(self, report_id: str) -> ExistingReport:
        """Retrieves a report by the report identifier.
        
        Raises an error if the report could not be found.
        
        Args:
            report_id (str): The report identifier to retrieve.
        """
        response = bearer_authenticated_session.get(f"{base_prefix}/{report_id}")
        response.raise_for_status()

        return ExistingReport.model_validate_json(response.json())

class ReportsWriteOnlyInterface:
    """Implements the write communication with the reports HTTP interface of an OpenADR 3 VTN."""

    def create_report(self, new_report: NewReport) -> ExistingReport:
        """Creates a report from the new report.
        
        Returns the created report response from the VTN as an ExistingReport.
        
        Args:
            new_report (NewReport): The new report to create.
        """
        with new_report.with_creation_guard():
            response = bearer_authenticated_session.post(base_prefix, data=new_report.model_dump_json())
            response.raise_for_status()
            return ExistingReport.model_validate_json(response.json())

    def update_report_by_id(self, report_id: str, updated_report: ExistingReport) -> ExistingReport:
        """Update the report with the report identifier in the VTN.

        If the report id does not match the id in the existing report, an error is
        raised.

        Returns the updated report response from the VTN.

        Args:
            report_id (str): The identifier of the report to update.
            updated_report (ExistingReport): The updated report.
        """
        if report_id != updated_report.id:
            raise ValueError("Report id does not match report id of updated report object.")
        
        # No lock on the ExistingReport type exists similar to the creation guard of a NewReport.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(f"{base_prefix}/{report_id}",
                                                    data=updated_report.model_dump_json())
        response.raise_for_status()
        return ExistingReport.model_validate_json(response.json())

    def delete_report_by_id(self, report_id: str) -> None:
        """Delete the report with the identifier in the VTN.

        Args:
            report_id (str): The identifier of the report to delete.
        """
        response = bearer_authenticated_session.delete(f"{base_prefix}/{report_id}")
        response.raise_for_status()

class ReportsInterface(ReportsReadOnlyInterface, ReportsWriteOnlyInterface):
    """Implements the read and write communication with the reports HTTP interface of an OpenADR 3 VTN."""