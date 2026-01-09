"""Contains the domain models related to attributes."""

from openadr3_client._models.common.value_map import ValueMap


class Attribute[T](ValueMap[str, T]):
    """Class representing an attribute."""
