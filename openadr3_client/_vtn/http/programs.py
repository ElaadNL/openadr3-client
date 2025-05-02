"""Implements the communication with the programs interface of an OpenADR 3 VTN."""

from pydantic.type_adapter import TypeAdapter

from openadr3_client._vtn.http.common._authenticated_session import bearer_authenticated_session
from openadr3_client._vtn.http.http_interface import HttpInterface
from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client._vtn.interfaces.programs import (
    ReadOnlyProgramsInterface,
    ReadWriteProgramsInterface,
    WriteOnlyProgramsInterface,
)
from openadr3_client.logging import logger
from openadr3_client.models.program.program import ExistingProgram, NewProgram

base_prefix = "programs"


class ProgramsReadOnlyHttpInterface(ReadOnlyProgramsInterface, HttpInterface):
    """Implements the read communication with the programs HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def get_programs(
        self, target: TargetFilter | None, pagination: PaginationFilter | None
    ) -> tuple[ExistingProgram, ...]:
        """
        Retrieve programs from the VTN.

        Args:
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.

        """
        query_params: dict = {}

        if target:
            query_params |= target.model_dump(by_alias=True, mode="json")

        if pagination:
            query_params |= pagination.model_dump(by_alias=True, mode="json")

        logger.debug("Programs - Performing get_programs request with query params: %s", query_params)

        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingProgram])
        return tuple(adapter.validate_python(response.json()))

    def get_program_by_id(self, program_id: str) -> ExistingProgram:
        """
        Retrieves a program by the program identifier.

        Raises an error if the program could not be found.

        Args:
            program_id (str): The program identifier to retrieve.

        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{program_id}")
        response.raise_for_status()

        return ExistingProgram.model_validate(response.json())


class ProgramsWriteOnlyHttpInterface(WriteOnlyProgramsInterface, HttpInterface):
    """Implements the write communication with the programs HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def create_program(self, new_program: NewProgram) -> ExistingProgram:
        """
        Creates a program from the new program.

        Returns the created program response from the VTN as an ExistingProgram.
        """
        with new_program.with_creation_guard():
            response = bearer_authenticated_session.post(
                f"{self.base_url}/{base_prefix}", json=new_program.model_dump(by_alias=True, mode="json")
            )
            response.raise_for_status()
            return ExistingProgram.model_validate(response.json())

    def update_program_by_id(self, program_id: str, updated_program: ExistingProgram) -> ExistingProgram:
        """
        Update the program with the program identifier in the VTN.

        If the program id does not match the id in the existing program, an error is
        raised.

        Returns the updated program response from the VTN.

        Args:
            program_id (str): The identifier of the program to update.
            updated_program (ExistingProgram): The updated program.

        """
        if program_id != updated_program.id:
            exc_msg = "Program id does not match program id of updated program object."
            raise ValueError(exc_msg)

        # No lock on the ExistingProgram type exists similar to the creation guard of a NewProgram
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(
            f"{self.base_url}/{base_prefix}/{program_id}", json=updated_program.model_dump(by_alias=True, mode="json")
        )
        response.raise_for_status()
        return ExistingProgram.model_validate(response.json())

    def delete_program_by_id(self, program_id: str) -> None:
        """
        Delete the program with the program identifier in the VTN.

        Args:
            program_id (str): The identifier of the program to delete.

        """
        response = bearer_authenticated_session.delete(f"{self.base_url}/{base_prefix}/{program_id}")
        response.raise_for_status()


class ProgramsHttpInterface(ReadWriteProgramsInterface, ProgramsReadOnlyHttpInterface, ProgramsWriteOnlyHttpInterface):
    """Implements the read and write communications with the programs HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
