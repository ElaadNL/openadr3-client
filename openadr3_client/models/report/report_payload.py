"""Contains the domain models related to event payloads."""

from enum import Enum
from typing import Any, final

from pydantic import Field, computed_field

from openadr3_client.models.common.payload import AllowedPayloadInputs, BasePayloadDescriptor, _BasePayload
from openadr3_client.models.common.unit import Unit


@final
class ReportReadingType(str, Enum):
    """Enumeration of the reading types of OpenADR 3."""

    DIRECT_READ = "DIRECT_READ"
    ESTIMATED = "ESTIMATED"
    SUMMED = "SUMMED"
    MEAN = "MEAN"
    PEAK = "PEAK"
    FORECAST = "FORECAST"
    AVERAGE = "AVERAGE"

    @classmethod
    def _missing_(cls: type["ReportReadingType"], value: Any) -> "ReportReadingType":  # noqa: ANN401
        """
        Add support for custom report reading type cases.

        Args:
            cls (type[&quot;EventPayloadType&quot;]): The report reading type class.
            value (Any): The custom enum value to add.

        Returns:
            ReportReadingType: The new report reading type.

        """
        # Create a new enum member dynamically
        new_member = str.__new__(cls, value)
        new_member._name_ = value
        new_member._value_ = value
        # Add it to the enum
        cls._member_map_[value] = new_member
        return new_member


@final
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

    @classmethod
    def _missing_(cls: type["ReportPayloadType"], value: Any) -> "ReportPayloadType":  # noqa: ANN401
        """
        Add support for custom report payload cases.

        Args:
            cls (type[&quot;EventPayloadType&quot;]): The report payload type class.
            value (Any): The custom enum value to add.

        Returns:
            ReportPayloadType: The new report payload type.

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

        exc_msg = f"Invalid report payload value: {value}"
        raise ValueError(exc_msg)


@final
class ReportPayloadDescriptor(BasePayloadDescriptor):
    """A description of the payload parameter."""

    payload_type: ReportPayloadType
    """The type of payload being described."""
    reading_type: ReportReadingType | None = None
    """The type of reading being described."""
    units: Unit | None = None
    """The units of the payload."""
    accuracy: float | None = None
    """The accuracy of the payload values."""
    confidence: int | None = Field(default=None, ge=0, le=100)

    @property
    @computed_field
    def object_type(self) -> str:
        """Returns the object type of the payload descriptor."""
        return "REPORT_PAYLOAD_DESCRIPTOR"


@final
class ReportPayload[T: AllowedPayloadInputs](_BasePayload[ReportPayloadType, T]):
    """The type of the report payload."""
