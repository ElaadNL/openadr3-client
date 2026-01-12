"""Contains the domain models related to targeting."""

from openadr3_client._models.common.value_map import ValueMap


class Target[T](ValueMap[str, T]):
    """Class representing a target."""
