# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

import random
import re
import string

import pytest
from pydantic import ValidationError

from openadr3_client._models.common.attribute import Attribute
from openadr3_client._models.common.value_map_collection import ValuesMap
from openadr3_client.oadr310.models.program.program import NewProgram
from openadr3_client.oadr310.models.program.program_attribute import ProgramAttributeType


def test_new_program_creation_guard() -> None:
    """
    Test that validates the NewProgram creation guard.

    The NewProgram creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method.
    """
    program = NewProgram(program_name="my-program")

    with program.with_creation_guard():
        pass  # simply pass through, without an exception.

    with (
        pytest.raises(ValueError, match=re.escape("CreationGuarded object has already been created.")),
        program.with_creation_guard(),
    ):
        pass


def test_new_program_too_long_name() -> None:
    """Test that validates that a program name can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewProgram(program_name=random_string)


def test_new_program_empty_program_name() -> None:
    """Test that validates that a program name cannot be an empty string."""
    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewProgram(program_name="")


def test_new_program_country_attribute_invalid() -> None:
    """
    Test that validates that a COUNTRY attribute must be ISO 3166-1 alpha-2 compliant.

    This test tries to use an invalid alpha-2 country code as attribute value.
    """
    with pytest.raises(ValidationError):
        _ = NewProgram(
            program_name="test-program",
            attributes=ValuesMap([Attribute(type=ProgramAttributeType.COUNTRY, values=("UT",))]),
        )


def test_new_program_country_attribute_valid() -> None:
    """Test that validates that a COUNTRY attribute accepts a valid ISO 3166-1 alpha-2 code."""
    _ = NewProgram(
        program_name="test-program",
        attributes=ValuesMap([Attribute(type=ProgramAttributeType.COUNTRY, values=("NL",))]),
    )


def test_new_program_division_attribute_invalid() -> None:
    """
    Test that validates that a PRINCIPAL_SUBDIVISION attribute must be ISO 3166-2 compliant.

    This test tries to use an invalid subdivision code.
    """
    with pytest.raises(ValidationError, match="is not a valid ISO 3166-2 division code for country"):
        _ = NewProgram(
            program_name="test-program",
            attributes=ValuesMap(
                [
                    Attribute(type=ProgramAttributeType.COUNTRY, values=("NL",)),
                    Attribute(type=ProgramAttributeType.PRINCIPAL_SUBDIVISION, values=("NL-UI",)),
                ]
            ),
        )


def test_new_program_division_attribute_valid() -> None:
    """Test that validates that a PRINCIPAL_SUBDIVISION attribute accepts a valid ISO 3166-2 code."""
    _ = NewProgram(
        program_name="test-program",
        attributes=ValuesMap(
            [
                Attribute(type=ProgramAttributeType.COUNTRY, values=("NL",)),
                Attribute(type=ProgramAttributeType.PRINCIPAL_SUBDIVISION, values=("NB",)),
            ]
        ),
    )


def test_new_program_subdivision_without_country_raises() -> None:
    """Test that PRINCIPAL_SUBDIVISION attribute without COUNTRY attribute raises a validation error."""
    with pytest.raises(ValidationError, match="PRINCIPAL_SUBDIVISION attribute cannot be set if COUNTRY attribute is not set"):
        _ = NewProgram(
            program_name="test-program",
            attributes=ValuesMap([Attribute(type=ProgramAttributeType.PRINCIPAL_SUBDIVISION, values=("NB",))]),
        )


def test_new_program_binding_events_boolean_valid() -> None:
    """Test that BINDING_EVENTS attribute accepts a boolean value."""
    _ = NewProgram(
        program_name="test-program",
        attributes=ValuesMap([Attribute(type=ProgramAttributeType.BINDING_EVENTS, values=(True,))]),
    )


def test_new_program_binding_events_non_boolean_raises() -> None:
    """Test that BINDING_EVENTS attribute with a non-boolean value raises a validation error."""
    with pytest.raises(ValidationError, match="BINDING_EVENTS attribute values must be boolean"):
        _ = NewProgram(
            program_name="test-program",
            attributes=ValuesMap([Attribute(type=ProgramAttributeType.BINDING_EVENTS, values=("true",))]),
        )


def test_new_program_custom_attribute_type() -> None:
    """Test that custom (non-standard) attribute types are accepted."""
    _ = NewProgram(
        program_name="test-program",
        attributes=ValuesMap([Attribute(type=ProgramAttributeType("MY_CUSTOM_ATTR"), values=("value",))]),
    )
