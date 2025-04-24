"""Contains the domain models related to event payloads."""

from enum import Enum
from typing import Literal

from pydantic import Field

from openadr3_client.domain.common.payload import _BasePayload
from openadr3_client.domain.model import ValidatableModel

class ReportReadingType(str, Enum):
    """Enumeration of the reading types of OpenADR 3."""

    DIRECT_READ = "DIRECT_READ"
    ESTIMATED = "ESTIMATED"
    SUMMED = "SUMMED"
    MEAN = "MEAN"
    PEAK = "PEAK"
    FORECAST = "FORECAST"
    AVERAGE = "AVERAGE"

class ReportPayloadType(str, Enum):
    """Enumeration of the report payload types of OpenADR 3."""

    READING = "READING"
    USAGE = "USAGE"
    DEMAND = "DEMAND"
    SETPOINT = "SETPOINT"
    DELTA_USAGE = "DELTA_USAGE"
    BASELINE = "BASELINE"
    OPERATING_STATE = "OPERATING_STATE"
    UP_REGULATION_AVAILABLE = "UP_REGULATION_AVAILABLE"
    DOWN_REGULATION_AVAILABLE = "DOWN_REGULATION_AVAILABLE"
    REGULATION_SETPOINT = "REGULATION_SETPOINT"
    STORAGE_USABLE_CAPACITY = "STORAGE_USABLE_CAPACITY"
    STORAGE_CHARGE_LEVEL = "STORAGE_CHARGE_LEVEL"
    STORAGE_MAX_DISCHARGE_POWER = "STORAGE_MAX_DISCHARGE_POWER"
    STORAGE_MAX_CHARGE_POWER = "STORAGE_MAX_CHARGE_POWER"
    SIMPLE_LEVEL = "SIMPLE_LEVEL"
    USAGE_FORECAST = "USAGE_FORECAST"
    STORAGE_DISPATCH_FORECAST = "STORAGE_DISPATCH_FORECAST"
    LOAD_SHED_DELTA_AVAILABLE = "LOAD_SHED_DELTA_AVAILABLE"
    GENERATION_DELTA_AVAILABLE = "GENERATION_DELTA_AVAILABLE"
    DATA_QUALITY = "DATA_QUALITY"
    IMPORT_RESERVATION_CAPACITY = "IMPORT_RESERVATION_CAPACITY"
    IMPORT_RESERVATION_FEE = "IMPORT_RESERVATION_FEE"
    EXPORT_RESERVATION_CAPACITY = "EXPORT_RESERVATION_CAPACITY"
    EXPORT_RESERVATION_FEE = "EXPORT_RESERVATION_FEE"

class ReportPayloadDescriptor(ValidatableModel):
    object_type = Literal["REPORT_PAYLOAD_DESCRIPTOR"]
    """The object type of the payload descriptor."""
    description: str
    """A description of the payload parameter."""
    payload_type: ReportPayloadType
    """The type of payload being described."""
    reading_type: ReportReadingType
    """The type of reading being described."""
    units: str
    """The units of the payload."""
    accuracy: float
    """The accuracy of the payload values."""
    confidence: int = Field(ge=0, le=100)


class ReportPayload[T](_BasePayload[ReportPayloadType, T]):
    """The type of the report payload."""

