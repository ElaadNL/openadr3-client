"""Contains the domain models related to targeting."""

from openadr3_client.domain.model import ValidatableModel


class Target[T](ValidatableModel):
    """Class representing a target for an event."""

    """The type of the target."""
    type: T

    """The value(s) of the target."""
    values: tuple[T, ...]
