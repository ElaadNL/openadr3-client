"""Module containing the base model for the input converter of the openadr3 client."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class OK:
    pass  # No fields for the validation


@dataclass
class ERROR:
    exception: ExceptionGroup


ValidationOutput = OK | ERROR


class BaseEventIntervalConverter[ROWTYPE, INPUTTYPE, OUTPUTTYPE](ABC):
    @abstractmethod
    def has_interval_period(self, row: ROWTYPE) -> bool: ...

    @abstractmethod
    def validate_input(self, given_input: INPUTTYPE) -> ValidationOutput: ...

    @abstractmethod
    def _do_convert(self, row_id: int, row: ROWTYPE) -> OUTPUTTYPE:
        """
        Convert a single row to the output type.

        Args:
            row_id (int): The id of the row.
            row (ROWTYPE): The row to convert.

        Returns:
            OUTPUTTYPE: The converted row.

        """
        ...

    @abstractmethod
    def _to_iterable(self, given_input: INPUTTYPE) -> Iterable[ROWTYPE]:
        """
        Convert the input to an iterable of rows.

        Args:
            given_input (INPUTTYPE): The input to convert.

        Returns:
            Iterable[ROWTYPE]: The iterable of rows.

        """
        ...

    def convert(self, given_input: INPUTTYPE) -> list[OUTPUTTYPE]:
        converted_output: list[OUTPUTTYPE] = []
        errors = []

        validation_result = self.validate_input(given_input)

        match validation_result:
            case ERROR(exception=e):
                raise e
            case OK():
                for i, row in enumerate(self._to_iterable(given_input)):
                    try:
                        converted_output.append(self._do_convert(i, row))
                    except Exception as e:  # noqa: BLE001
                        errors.append(e)

                if errors:
                    err_msg = "Conversion validation errors occurred"
                    raise ExceptionGroup(err_msg, errors)

        return converted_output
