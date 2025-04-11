"""Contains the domain models related to targeting."""

from typing import Tuple
from openadr3_client.domain.base_model import BaseModel


class Target[T](BaseModel):
    """Class representing a target for an event."""

    """The type of the target."""
    type: T

    """The value(s) of the target."""
    values: Tuple[T, ...]
