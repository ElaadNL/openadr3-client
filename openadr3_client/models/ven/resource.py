from abc import ABC
from typing import final

from pydantic import AwareDatetime, Field

from openadr3_client.models._base_model import BaseModel
from openadr3_client.models.common.attribute import Attribute
from openadr3_client.models.common.creation_guarded import CreationGuarded
from openadr3_client.models.common.target import Target
from openadr3_client.models.model import ValidatableModel


class Resource[T](ABC, ValidatableModel):
    """Class representing a resource, which is subject to control by a ven."""

    id: T
    """Identifier of the resource."""

    resource_name: str = Field(min_length=1, max_length=128)
    """The name of the resource."""

    ven_id: str = Field(alias="venID", min_length=1, max_length=128)
    """The identifier of the ven this resource belongs to."""

    attributes: tuple[Attribute, ...] | None = None
    """The attributes of the resource."""

    targets: tuple[Target, ...] | None = None
    """The targets of the resource."""


@final
class NewResource(Resource[None], CreationGuarded):
    """Class representing a new resource not yet pushed to the VTN."""


@final
class ResourceUpdate(BaseModel):
    """Class representing an update to a resource."""

    resource_name: str | None = Field(default=None, min_length=1, max_length=128)
    """The name of the resource."""

    ven_id: str | None = Field(alias="venID", default=None, min_length=1, max_length=128)
    """The identifier of the ven this resource belongs to."""

    attributes: tuple[Attribute, ...] | None = None
    """The attributes of the resource."""

    targets: tuple[Target, ...] | None = None
    """The targets of the resource."""


@final
class ExistingResource(Resource[str]):
    """Class representing an existing report retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    def update(self, update: ResourceUpdate) -> "ExistingResource":
        """
        Update the existing resource with the provided update.

        Args:
            update (ResourceUpdate): The update to apply to the resource.

        Returns:
            ExistingResource: The updated resource.

        """
        current_resource = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_resource = current_resource | update_dict
        return ExistingResource(**updated_resource)
