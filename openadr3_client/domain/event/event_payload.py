"""Contains the domain models related to event payloads."""

from abc import ABC
from enum import Enum
from typing import Literal

from pydantic import field_validator

from openadr3_client.domain.common.payload import _BasePayload
from openadr3_client.domain.model import ValidatableModel


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


class EventPayloadDescriptor(ValidatableModel):
    """A description explaining the payload."""
    object_type = Literal["EVENT_PAYLOAD_DESCRIPTOR"]
    """The object type of the payload descriptor."""
    description: str
    """A description of the payload parameter."""
    payload_type: EventPayloadType
    """The type of payload being described."""
    units: str
    """The units of the payload."""
    currency: str
    """The currency of the payload."""

class EventPayload[T](_BasePayload[EventPayloadType, T]):
    """The type of the event payload."""