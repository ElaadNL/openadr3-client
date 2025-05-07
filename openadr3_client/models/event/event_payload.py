"""Contains the domain models related to event payloads."""

from enum import Enum
from typing import Any, final

from pydantic import computed_field
from pydantic_extra_types.currency_code import ISO4217

from openadr3_client.models.common.payload import AllowedPayloadInputs, BasePayloadDescriptor, _BasePayload


class EventPayloadType(str, Enum):
    """Enumeration of the event payload types of OpenADR 3."""

    SIMPLE = "SIMPLE"
    PRICE = "PRICE"
    CHARGE_STATE_SETPOINT = "CHARGE_STATE_SETPOINT"
    DISPATCH_SETPOINT = "DISPATCH_SETPOINT"
    DISPATCH_SETPOINT_RELATIVE = "DISPATCH_SETPOINT_RELATIVE"
    CONTROL_SETPOINT = "CONTROL_SETPOINT"
    EXPORT_PRICE = "EXPORT_PRICE"
    GHG = "GHG"
    CURVE = "CURVE"
    OLS = "OLS"
    IMPORT_CAPACITY_SUBSCRIPTION = "IMPORT_CAPACITY_SUBSCRIPTION"
    IMPORT_CAPACITY_RESERVATION = "IMPORT_CAPACITY_RESERVATION"
    IMPORT_CAPACITY_RESERVATION_FEE = "IMPORT_CAPACITY_RESERVATION_FEE"
    IMPORT_CAPACITY_AVAILABLE = "IMPORT_CAPACITY_AVAILABLE"
    IMPORT_CAPACITY_AVAILABLE_PRICE = "IMPORT_CAPACITY_AVAILABLE_PRICE"
    EXPORT_CAPACITY_SUBSCRIPTION = "EXPORT_CAPACITY_SUBSCRIPTION"
    EXPORT_CAPACITY_RESERVATION = "EXPORT_CAPACITY_RESERVATION"
    EXPORT_CAPACITY_RESERVATION_FEE = "EXPORT_CAPACITY_RESERVATION_FEE"
    EXPORT_CAPACITY_AVAILABLE = "EXPORT_CAPACITY_AVAILABLE"
    EXPORT_CAPACITY_AVAILABLE_PRICE = "EXPORT_CAPACITY_AVAILABLE_PRICE"
    IMPORT_CAPACITY_LIMIT = "IMPORT_CAPACITY_LIMIT"
    EXPORT_CAPACITY_LIMIT = "EXPORT_CAPACITY_LIMIT"
    ALERT_GRID_EMERGENCY = "ALERT_GRID_EMERGENCY"
    ALERT_BLACK_START = "ALERT_BLACK_START"
    ALERT_POSSIBLE_OUTAGE = "ALERT_POSSIBLE_OUTAGE"
    ALERT_FLEX_ALERT = "ALERT_FLEX_ALERT"
    ALERT_FIRE = "ALERT_FIRE"
    ALERT_FREEZING = "ALERT_FREEZING"
    ALERT_WIND = "ALERT_WIND"
    ALERT_TSUNAMI = "ALERT_TSUNAMI"
    ALERT_AIR_QUALITY = "ALERT_AIR_QUALITY"
    ALERT_OTHER = "ALERT_OTHER"
    CTA2045_REBOOT = "CTA2045_REBOOT"
    CTA2045_SET_OVERRIDE_STATUS = "CTA2045_SET_OVERRIDE_STATUS"

    @classmethod
    def _missing_(cls: type["EventPayloadType"], value: Any) -> "EventPayloadType":  # noqa: ANN401
        """
        Add support for custom event payload cases.

        Args:
            cls (type[&quot;EventPayloadType&quot;]): The event payload type class.
            value (Any): The custom enum value to add.

        Returns:
            EventPayloadType: The new event payload type.

        """
        min_length = 1
        max_length = 128
        if isinstance(value, str) and min_length <= len(value) <= max_length:
            # Create a new enum member dynamically
            new_member = str.__new__(cls, value)
            new_member._name_ = value
            new_member._value_ = value
            # Add it to the enum
            cls._member_map_[value] = new_member
            return new_member
        exc_msg = f"Invalid event payload value: {value}"
        raise ValueError(exc_msg)


@final
class EventPayloadDescriptor(BasePayloadDescriptor):
    """A description of the payload parameter."""

    payload_type: EventPayloadType
    """The type of payload being described."""
    units: str | None = None
    """The units of the payload."""
    currency: ISO4217 | None = None
    """The currency of the payload."""

    @property
    @computed_field
    def object_type(self) -> str:
        """Returns the object type of the payload descriptor."""
        return "EVENT_PAYLOAD_DESCRIPTOR"


@final
class EventPayload[T: AllowedPayloadInputs](_BasePayload[EventPayloadType, T]):
    """The type of the event payload."""
