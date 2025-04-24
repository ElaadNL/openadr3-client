"""Implements the communication with the programs interface of an OpenADR 3 VTN."""

from typing import List, Tuple

from pydantic.type_adapter import TypeAdapter
from openadr3_client.vtn.common.filters import PaginationFilter, TargetFilter
from openadr3_client.domain.program.program import ExistingProgram, NewProgram
from openadr3_client.vtn.common._authenticated_session import bearer_authenticated_session

from dataclasses import asdict

base_prefix = "/programs"

class ProgramsReadOnlyInterface:
    """Implements the read communication with the programs HTTP interface of an OpenADR 3 VTN."""

    def get_programs(self, target: TargetFilter, pagination: PaginationFilter) -> Tuple[ExistingProgram, ...]:
        """Retrieve programs from the VTN"""

        # Convert the filters to dictionaries and union them. No key clashing can happen, as the properties
        # of the filters are unique.
        query_params = asdict(target) | asdict(pagination)

        response = bearer_authenticated_session.get(f"{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(List[ExistingProgram])
        return tuple(adapter.validate_json(response.json()))

    def get_program_by_id(self, program_id: str) -> ExistingProgram:
        """Retrieves a program by the program identifier.
        
        Raises an error if the program could not be found."""
        response = bearer_authenticated_session.get(f"{base_prefix}/{program_id}")
        response.raise_for_status()

        return ExistingProgram.model_validate_json(response.json())

class ProgramsWriteOnlyInterface:
    """Implements the write communication with the programs HTTP interface of an OpenADR 3 VTN."""

    def create_program(self, new_program: NewProgram) -> ExistingProgram:
        """Creates a program from the new program.
        
        Returns the created program response from the VTN as an ExistingProgram."""
        with new_program.with_creation_guard():
            response = bearer_authenticated_session.post(base_prefix, data=new_program.model_dump_json())
            response.raise_for_status()
            return ExistingProgram.model_validate_json(response.json())

    def update_program_by_id(self, program_id: str, updated_program: ExistingProgram) -> ExistingProgram:
        """Update the program with the program identifier in the VTN.

        If the program id does not match the id in the existing program, an error is
        raised.

        Returns the updated program response from the VTN.

        Args:
            program_id (str): The identifier of the program to update.
            updated_program (ExistingProgram): The updated program.
        """
        if program_id != updated_program.id:
            raise ValueError("Program id does not match program id of updated program object.")
        
        # No lock on the ExistingProgram type exists similar to the creation guard of a NewProgram
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(f"{base_prefix}/{program_id}",
                                                    data=updated_program.model_dump_json())
        response.raise_for_status()
        return ExistingProgram.model_validate_json(response.json())

    def delete_program_by_id(self, program_id: str) -> None:
        """Delete the program with the program identifier in the VTN.

        Args:
            program_id (str): The identifier of the program to delete.
        """
        response = bearer_authenticated_session.delete(f"{base_prefix}/{program_id}")
        response.raise_for_status()

class ProgramsInterface(ProgramsReadOnlyInterface, ProgramsWriteOnlyInterface):
    """Implements the read and write communications with the programs HTTP interface of an OpenADR 3 VTN."""