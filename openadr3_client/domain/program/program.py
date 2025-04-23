"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from contextlib import contextmanager
from threading import Lock
from typing import TYPE_CHECKING

import pycountry
from pydantic import AnyUrl, AwareDatetime, Field, PrivateAttr, field_validator
from pydantic_extra_types.country import CountryAlpha2

from openadr3_client.domain.common.interval_period import IntervalPeriod
from openadr3_client.domain.common.target import Target
from openadr3_client.domain.event.event_payload import EventPayloadDescriptor
from openadr3_client.domain.model import ValidatableModel

if TYPE_CHECKING:
    from collections.abc import Iterator


class Program[T](ABC, ValidatableModel):
    """Base class for programs."""

    id: T
    """The identifier for the program."""

    program_name: str = Field(min_length=1, max_length=128)
    """The name of the program.

    Must be between 1 and 128 characters long."""

    program_long_name: str | None = None
    """The optional long name of the program."""

    retailer_name: str | None = None
    """The optional energy retailer name of the program."""

    retailer_long_name: str | None = None
    """The optional energy retailer long name of the program."""

    program_type: str | None = None
    """The optional program type of the program."""

    country: CountryAlpha2 | None = None
    """The optional alpha-2 country code for the program."""

    principal_sub_division: str | None = None
    """The optional ISO-3166-2 coding, for example state in the US."""

    interval_period: IntervalPeriod | None = None
    """The interval period of the program."""

    program_descriptions: tuple[AnyUrl, ...] | None = None
    """An optional list of program descriptions for the program.

    The specification of OpenADR 3.0.1. describes the following:
    List of URLs to human and/or machine-readable content.
    """

    binding_events: bool | None = None
    """Whether events inside the program are considered immutable."""

    local_price: bool | None = None
    """Whether the price of the events is local.

    Typically true if events have been adapted from a grid event.
    """

    payload_descriptor: tuple[EventPayloadDescriptor, ...] | None = None
    """The event payload descriptors of the program."""

    targets: tuple[Target, ...] | None = None
    """The targets of the program."""

    @field_validator("principal_sub_division")
    def validate_iso_3166_2(self, v: str | None) -> str | None:
        """Validates that principal_sub_division is iso-3166-2 compliant."""
        if v and not pycountry.subdivisions.match(v):
            exc_msg = f"{v} is not a valid ISO 3166-2 division code."
            raise ValueError(exc_msg)
        return v


class NewProgram(Program[None]):
    """Class representing a new program not yet pushed to the VTN."""

    """Private flag to track if NewProgram has been used to create an program in the VTN.

    If this flag is set to true, calls to create a program inside the VTN with
    this NewProgram object will be rejected."""
    _created: bool = PrivateAttr(default=False)

    """Lock object to synchronize access to with_creation_guard."""
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @contextmanager
    def with_creation_guard(self) -> Iterator[None]:
        """
        A guard which enforces that a NewProgram can only be used once.

        A NewProgram can only be used to create a program inside a VTN exactly once.
        Subsequent calls to create the program with the same object will raise an
        exception.

        Raises:
            ValueError: Raised if the NewProgram has already been created inside the VTN.

        """
        with self._lock:
            if self._created:
                err_msg = "NewProgram has already been created."
                raise ValueError(err_msg)

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise


class ExistingProgram(Program[str]):
    """Class representing an existing program retrieved from the VTN."""

    created_datetime: AwareDatetime
    modification_datetime: AwareDatetime
