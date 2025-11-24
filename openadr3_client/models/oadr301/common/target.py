"""Contains the domain models related to targeting."""

from openadr3_client.models.oadr301.common.value_map import ValueMap


class Target[T](ValueMap[str, T]):
    """Class representing a target."""
