import random
import re
import string

import pytest
from pydantic import ValidationError

from openadr3_client.models.oadr310.resource.resource import NewResource


def test_new_resource_creation_guard() -> None:
    """
    Test that validates the NewResource creation guard.

    The NewResource creation guard should only allow invocation inside the context manager
    exactly once if no exception is raised in the yield method.
    """
    resource = NewResource(resource_name="TestResource", venID="ven123")

    with resource.with_creation_guard():
        pass  # simply pass through, without an exception.

    with (
        pytest.raises(ValueError, match=re.escape("CreationGuarded object has already been created.")),
        resource.with_creation_guard(),
    ):
        pass


def test_resource_ven_id_too_long() -> None:
    """Test that validates that the ven id of a resource can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewResource(resource_name="TestResource", venID=random_string)


def test_resource_ven_id_empty_string() -> None:
    """Test that validates that the ven id of a resource cannot be an empty string."""
    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewResource(resource_name="TestResource", venID="")


def test_resource_name_too_long() -> None:
    """Test that validates that the resource name of a resource can only be 128 characters max."""
    length = 129
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=length))

    with pytest.raises(ValidationError, match="String should have at most 128 characters"):
        _ = NewResource(resource_name=random_string, venID="ven-id")


def test_resource_name_empty_string() -> None:
    """Test that validates that the resource name of a resource cannot be an empty string."""
    with pytest.raises(ValidationError, match="have at least 1 character"):
        _ = NewResource(resource_name="", venID="ven-id")
