from abc import ABC, abstractmethod

from pydantic import computed_field, field_validator

from openadr3_client.models.common.value_map import ValueMap
from openadr3_client.models.model import ValidatableModel


class BasePayloadDescriptor(ABC, ValidatableModel):
    """Base class for a payload descriptor."""

    @property
    @abstractmethod
    @computed_field
    def object_type(self) -> str:
        """Returns the object type of the payload descriptor."""


class Point(ValidatableModel):
    """A point in a 2D space."""

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        """
        Constructs a point.

        Args:
            x (float): The x coordinate.
            y (float): The y coordinate.

        """
        self.x = x
        self.y = y


AllowedPayloadInputs = int | float | str | bool | Point


class _BasePayload[PAYLOAD_TYPE, T: AllowedPayloadInputs](ABC, ValueMap[PAYLOAD_TYPE, T]):
    """Represents a generic payload of OpenADR 3."""

    @field_validator("values", mode="after")
    @classmethod
    def payload_atleast_one(cls, values: tuple[T, ...]) -> tuple[T, ...]:
        """
        Validates that atleast one value must be present inside the payload.

        Args:
            values (tuple[T, ...]): The values of the payload.

        Raises:
            ValueError: Raised if the payload does not have one or more values.

        """
        if len(values) == 0:
            err_msg = "payload must contain at least one value."
            raise ValueError(err_msg)
        return values


class StringPayload[PAYLOAD_TYPE](_BasePayload[PAYLOAD_TYPE, str]):
    """A string payload."""


class IntPayload[PAYLOAD_TYPE](_BasePayload[PAYLOAD_TYPE, int]):
    """An integer payload."""


class FloatPayload[PAYLOAD_TYPE](_BasePayload[PAYLOAD_TYPE, float]):
    """A float payload."""


class BoolPayload[PAYLOAD_TYPE](_BasePayload[PAYLOAD_TYPE, bool]):
    """A boolean payload."""


class PointPayload[PAYLOAD_TYPE](_BasePayload[PAYLOAD_TYPE, Point]):
    """A point payload."""
