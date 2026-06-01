# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the domain types related to events."""

from __future__ import annotations

from abc import ABC
from typing import final

import pycountry
from pydantic import AnyUrl, AwareDatetime, Field, TypeAdapter, model_validator
from pydantic_extra_types.country import CountryAlpha2

from openadr3_client._models._base_model import BaseModel
from openadr3_client._models._validatable_model import OpenADRResource
from openadr3_client._models.common.attribute import Attribute
from openadr3_client._models.common.creation_guarded import CreationGuarded
from openadr3_client._models.common.interval_period import IntervalPeriod
from openadr3_client._models.common.value_map_collection import ValuesMap
from openadr3_client.oadr310.models.event.event_payload import EventPayloadDescriptor
from openadr3_client.oadr310.models.program.program_attribute import ProgramAttributeType


def _validate_binding_events(attributes: ValuesMap) -> None:  # type: ignore[type-arg]
    attr = attributes.get_by_type(ProgramAttributeType.BINDING_EVENTS)
    if attr is None:
        return
    for val in attr.values:
        if not isinstance(val, bool):
            exc_msg = f"BINDING_EVENTS attribute values must be boolean, got: {type(val).__name__}"
            raise ValueError(exc_msg)  # noqa: TRY004


def _validate_country_subdivision(attributes: ValuesMap[ProgramAttributeType]) -> None:  # type: ignore[type-arg]
    country_attr = attributes.get_by_type(ProgramAttributeType.COUNTRY)
    subdivision_attr = attributes.get_by_type(ProgramAttributeType.PRINCIPAL_SUBDIVISION)

    if country_attr is not None:
        TypeAdapter(CountryAlpha2).validate_python(country_attr.values[0])

    if subdivision_attr is None:
        return

    if country_attr is None:
        exc_msg = "PRINCIPAL_SUBDIVISION attribute cannot be set if COUNTRY attribute is not set."
        raise ValueError(exc_msg)

    country = country_attr.values[0]
    subdivisions_of_country = pycountry.subdivisions.get(country_code=country) or []
    principals_only = [s.code.split("-")[-1] for s in subdivisions_of_country]

    for subdivision in subdivision_attr.values:
        if subdivision not in principals_only:
            exc_msg = f"{subdivision} is not a valid ISO 3166-2 division code for country {country}."
            raise ValueError(exc_msg)


class ProgramDescription(BaseModel):  # type: ignore[call-arg]
    """Class representing a URL object."""

    url: AnyUrl = Field(validation_alias="URL", serialization_alias="URL")
    """The URL."""


class _ProgramBase(BaseModel):
    """Base class containing common properties for Program and ProgramUpdate."""

    program_name: str = Field(min_length=1, max_length=128)
    """The name of the program.

    Must be between 1 and 128 characters long."""

    interval_period: IntervalPeriod | None = None
    """The interval period of the program."""

    program_descriptions: tuple[ProgramDescription, ...] | None = None
    """An optional list of program descriptions for the program.

    The specification of OpenADR 3.0.1. describes the following:
    List of URLs to human and/or machine-readable content.
    """

    payload_descriptors: tuple[EventPayloadDescriptor, ...] | None = None
    """The event payload descriptors of the program."""

    targets: tuple[str, ...] | None = None
    """The targets of the program."""

    attributes: ValuesMap[ProgramAttributeType, Attribute] | None = None
    """The attributes of the program."""

    @model_validator(mode="after")
    def validate_attributes(self) -> _ProgramBase:
        """Validate program-specific attribute constraints."""
        if not self.attributes:
            return self
        _validate_binding_events(self.attributes)
        _validate_country_subdivision(self.attributes)
        return self


class Program(ABC, OpenADRResource, _ProgramBase):
    """Base class for programs."""

    @property
    def name(self) -> str:
        """Helper method to get the name field of the model."""
        return self.program_name


@final
class ProgramUpdate(_ProgramBase):
    """Class representing an update to a program."""


@final
class NewProgram(Program, CreationGuarded):
    """Class representing a new program not yet pushed to the VTN."""


class ServerProgram(Program):
    """Class representing a program retrieved from the VTN."""

    id: str
    """The identifier for the program."""
    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime


@final
class ExistingProgram(ServerProgram):
    """Class representing an existing program retrieved from the VTN."""

    def update(self, update: ProgramUpdate) -> ExistingProgram:
        """
        Update the existing program with the provided update.

        Args:
            update: The update to apply to the program.

        Returns:
            The updated program.

        """
        current_program = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_program = current_program | update_dict
        return ExistingProgram(**updated_program)


@final
class DeletedProgram(ServerProgram):
    """Class representing a deleted program."""
