from openadr3_client._models._validatable_model import ValidatableModel


class ValueMap[TYPE, VALUETYPE](ValidatableModel):
    """
    Class representing an OpenADR3 value map.

    A value map is one or more values associated with a specific type.
    """

    type: TYPE
    """The type of the value map."""

    values: tuple[VALUETYPE, ...]
    """The value(s) of the value map."""
