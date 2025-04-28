"""Implements the abstract base class for the programs VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.program.program import ExistingProgram, NewProgram


class ReadOnlyProgramsInterface(ABC):
    """Abstract class which contains the interface for read only methods of programs."""

    @abstractmethod
    def get_programs(
        self, target: TargetFilter | None, pagination: PaginationFilter | None
    ) -> tuple[ExistingProgram, ...]:
        """
        Retrieve programs from the VTN.

        Args:
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.

        """

    @abstractmethod
    def get_program_by_id(self, program_id: str) -> ExistingProgram:
        """
        Retrieves a program by the program identifier.

        Raises an error if the program could not be found.

        Args:
            program_id (str): The program identifier to retrieve.

        """


class WriteOnlyProgramsInterface(ABC):
    """Abstract class which contains the interface for write only methods of programs."""

    @abstractmethod
    def create_program(self, new_program: NewProgram) -> ExistingProgram:
        """
        Creates a program from the new program.

        Returns the created program response from the VTN as an ExistingProgram.
        """

    @abstractmethod
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

    @abstractmethod
    def delete_program_by_id(self, program_id: str) -> None:
        """
        Delete the program with the program identifier in the VTN.

        Args:
            program_id (str): The identifier of the program to delete.

        """


class ReadWriteProgramsInterface(ReadOnlyProgramsInterface, WriteOnlyProgramsInterface):
    """Class which allows both read and write access on the resource."""
