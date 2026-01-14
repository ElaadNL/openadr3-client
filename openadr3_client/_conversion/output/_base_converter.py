# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Module containing the base model for the output converter."""

from abc import ABC, abstractmethod


class BaseOutputConverter[InputType, OutputType](ABC):
    @abstractmethod
    def convert(self, given_input: InputType) -> OutputType:
        """
        Convert the input to the output type.

        Args:
            given_input: The input to convert.

        Returns: The converted output.

        """
        ...
