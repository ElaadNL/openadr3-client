import random
import string

import pytest
from pydantic import ValidationError

from openadr3_client.domain.program.program import NewProgram


def test_new_program_creation_guard() -> None:
    """
    Test that validates the NewProgram creation guard.

    The NewProgram creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method.
    """
    program = NewProgram(id=None, program_name="my-program")

    with program.with_creation_guard():
        pass  # simply pass through, without an exception.

    with pytest.raises(ValueError, match="NewProgram has already been created."), program.with_creation_guard():
        pass


def test_new_program_too_long_name() -> None:
    """Test that validates that a program name can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewProgram(id=None, program_name=random_string)


def test_new_program_empty_program_name() -> None:
    """Test that validates that a program name cannot be an empty string."""
    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewProgram(id=None, program_name="")


def test_new_program_country_code_invalid() -> None:
    """
    Test that validates that a country code of a program must be ISO 3166-1 alpha-2 compliant.

    This test tries to use an invalid alpha-2 country code.
    """
    with pytest.raises(ValidationError, match="Invalid country alpha2 code"):
        _ = NewProgram(id=None, program_name="test-program", country="UT")  # type: ignore[arg-type]


def test_new_program_country_code_valid() -> None:
    """
    Test that validates that a country code of a program must be ISO 3166-1 alpha-2 compliant.

    This test tries to use a valid alpha-2 country code.
    """
    _ = NewProgram(id=None, program_name="test-program", country="NL")  # type: ignore[arg-type]


def test_new_program_division_invalid() -> None:
    """
    Test that validates that a principal_sub_division of a program must be ISO-3166-2 compliant.

    This test tries to use an invalid alpha-2 country code.
    """
    with pytest.raises(ValidationError, match="is not a valid ISO 3166-2 division code for the program country"):
        _ = NewProgram(id=None, program_name="test-program", country="NL", principal_sub_division="NL-UI")  # type: ignore[arg-type]


def test_new_program_division_valid() -> None:
    """
    Test that validates that a principal_sub_division of a program must be ISO-3166-2 compliant.

    This test tries to use a valid ISO-3166-2 province.
    """
    _ = NewProgram(id=None, program_name="test-program", country="NL", principal_sub_division="NB")  # type: ignore[arg-type]
