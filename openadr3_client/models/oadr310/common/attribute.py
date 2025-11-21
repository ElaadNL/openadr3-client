"""Contains the domain models related to attributes."""

from openadr3_client.models.oadr310.common.value_map import ValueMap


class Attribute[T](ValueMap[str, T]):
    """Class representing an attribute."""
