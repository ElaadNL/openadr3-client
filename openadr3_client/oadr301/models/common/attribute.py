"""Contains the domain models related to attributes."""

from openadr3_client.oadr301.models.common.value_map import ValueMap


class Attribute[T](ValueMap[str, T]):
    """Class representing an attribute."""
