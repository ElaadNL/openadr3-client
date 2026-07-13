# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Domain models for NLFlex resource groups."""

from abc import ABC
from typing import Literal, final

from pydantic import AwareDatetime, Field

from openadr3_client._models._base_model import BaseModel
from openadr3_client._models._validatable_model import OpenADRResource
from openadr3_client._models.common.attribute import Attribute
from openadr3_client._models.common.creation_guarded import CreationGuarded
from openadr3_client._models.common.value_map_collection import ValuesMap
from openadr3_client._models.common.ven_resource_attribute_type import VenResourceAttributeType


class ResourceGroupChild(BaseModel):
    """A typed reference to a child member of a resource group (by object ID)."""

    type: Literal["ven_resource", "resource_group"]
    """Whether the child is a VEN resource or a nested resource group."""

    id: str = Field(min_length=1, max_length=128)
    """Object ID of the referenced resource or nested resource group."""


class _ResourceGroupBase(BaseModel):
    """Common properties shared by resource group requests and server objects."""

    resource_group_name: str = Field(min_length=1, max_length=128)
    """The name of the resource group. Expected unique within a VTN."""

    targets: tuple[str, ...] = ()
    """Target strings used to classify or filter the resource group."""

    attributes: ValuesMap[VenResourceAttributeType, Attribute] | None = None
    """The attributes of the resource group."""

    children: tuple[ResourceGroupChild, ...] = ()
    """Child members of the resource group.

    A VEN reading a group receives only the children whose resource belongs to that VEN;
    other VENs' members are obfuscated (omitted) server-side. This tuple therefore tolerates
    fewer entries than the group actually contains."""


class ResourceGroup(ABC, OpenADRResource, _ResourceGroupBase):
    """Class representing a resource group."""

    @property
    def name(self) -> str:
        """Helper to get the name field of the model."""
        return self.resource_group_name


@final
class NewResourceGroup(ResourceGroup, CreationGuarded):
    """A resource group not yet pushed to the VTN by a BL client."""

    object_type: Literal["RESOURCE_GROUP"] = Field(default="RESOURCE_GROUP")
    """The object type."""


@final
class ResourceGroupUpdate(_ResourceGroupBase):
    """An update to a resource group by a BL client."""

    object_type: Literal["RESOURCE_GROUP"] = Field(default="RESOURCE_GROUP")
    """The object type."""


class ServerResourceGroup(ResourceGroup):
    """A resource group retrieved from the VTN, carrying server-provided metadata."""

    id: str
    """Identifier of the resource group."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    object_type: Literal["RESOURCE_GROUP"] = Field(default="RESOURCE_GROUP")
    """The object type."""


@final
class ExistingResourceGroup(ServerResourceGroup):
    """An existing resource group retrieved from the VTN."""

    def update(self, update: ResourceGroupUpdate) -> "ExistingResourceGroup":
        """
        Apply the provided update and return the updated resource group.

        Args:
            update: The update to apply.

        Returns:
            The updated resource group.

        """
        current = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        return ExistingResourceGroup(**(current | update_dict))


@final
class DeletedResourceGroup(ServerResourceGroup):
    """A deleted resource group returned by the VTN on delete."""
