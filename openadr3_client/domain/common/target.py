"""Contains the domain models related to targeting."""

from openadr3_client.domain.common.value_map import ValueMap


# TODO: CHECK IF THERE ARE CONSTRAINTS ON TYPE PARAM FOR TARGET AND ATTRIBUTES
class Target[T](ValueMap[str, T]):
    """Class representing a target."""
