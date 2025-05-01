import random
import string

import pytest
from pydantic import ValidationError

from openadr3_client.models.ven.ven import NewVen


def test_new_ven_creation_guard() -> None:
    """
    Test that validates the NewVen creation guard.

    The NewVen creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method.
    """
    ven = NewVen(id=None, ven_name="test-ven")

    with ven.with_creation_guard():
        pass  # simply pass through, without an exception.

    with pytest.raises(ValueError, match="NewVen has already been created."), ven.with_creation_guard():
        pass


def test_ven_name_too_long() -> None:
    """Test that validates that the ven name of a ven can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewVen(id=None, ven_name=random_string)


def test_ven_name_empty_string() -> None:
    """Test that validates that the ven name of a ven cannot be an empty string."""
    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewVen(id=None, ven_name="")
