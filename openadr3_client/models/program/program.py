"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from typing import final

import pycountry
from pydantic import AnyUrl, AwareDatetime, Field, model_validator
from pydantic_extra_types.country import CountryAlpha2

from openadr3_client.models._base_model import BaseModel
from openadr3_client.models.common.creation_guarded import CreationGuarded
from openadr3_client.models.common.interval_period import IntervalPeriod
from openadr3_client.models.common.target import Target
from openadr3_client.models.event.event_payload import EventPayloadDescriptor
from openadr3_client.models.model import ValidatableModel


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

    @model_validator(mode="after")
    def validate_iso_3166_2(self) -> Program:
        """
        Validates that principal_sub_division is iso-3166-2 compliant.

        The principal_sub_division is typically part of the ISO-3166 country code.
        However, OpenADR has opted to split this ISO-3166 code into the ISO-3166-1
        and ISO-3166-2 codes.

        For example, the ISO-3166-1 code for the United States is "US".
        The ISO-3166-2 code for the state of California is "CA".
        """
        if self.principal_sub_division:
            if not self.country:
                exc_msg = "principal sub division cannot be set if country is not set."
                raise ValueError(exc_msg)
            subdivisions_of_country = pycountry.subdivisions.get(country_code=self.country)

            principals_only = [subdivision.code.split("-")[-1] for subdivision in subdivisions_of_country]

            if self.principal_sub_division not in principals_only:
                exc_msg = (
                    f"{self.principal_sub_division} is not a valid ISO 3166-2 "
                    "division code for the program country {self.country}."
                    ""
                )
                raise ValueError(exc_msg)

        return self


@final
class ProgramUpdate(BaseModel):
    """Class representing an update to a program."""

    program_name: str | None = Field(default=None, min_length=1, max_length=128)
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


@final
class NewProgram(Program[None], CreationGuarded):
    """Class representing a new program not yet pushed to the VTN."""


@final
class ExistingProgram(Program[str]):
    """Class representing an existing program retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    def update(self, update: ProgramUpdate) -> ExistingProgram:
        """
        Update the existing program with the provided update.

        Args:
            update (ProgramUpdate): The update to apply to the program.

        Returns:
            ExistingProgram: The updated program.

        """
        current_program = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_program = current_program | update_dict
        return ExistingProgram(**updated_program)
