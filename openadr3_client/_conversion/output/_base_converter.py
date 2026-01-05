"""Module containing the base model for the output converter."""

from abc import ABC, abstractmethod


class BaseOutputConverter[InputType, OutputType](ABC):
    @abstractmethod
    def convert(self, given_input: InputType) -> OutputType:
        """
        Convert the input to the output type.

        Args:
            given_input (InputType): The input to convert.

        Returns: The converted output.

        """
        ...
