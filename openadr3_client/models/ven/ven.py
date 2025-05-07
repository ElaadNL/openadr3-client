from abc import ABC
from typing import final

from pydantic import AwareDatetime, Field

from openadr3_client.models._base_model import BaseModel
from openadr3_client.models.common.attribute import Attribute
from openadr3_client.models.common.creation_guarded import CreationGuarded
from openadr3_client.models.common.target import Target
from openadr3_client.models.model import ValidatableModel
from openadr3_client.models.ven.resource import ExistingResource


class Ven[T](ABC, ValidatableModel):
    """Base class for vens."""

    id: T
    """The identifier of the ven object."""

    ven_name: str = Field(min_length=1, max_length=128)
    """The ven name of the ven object."""

    attributes: tuple[Attribute, ...] | None = None
    """The attributes of the ven."""

    targets: tuple[Target, ...] | None = None
    """The targets of the ven object."""

    resources: tuple[ExistingResource, ...] | None = None
    """The resources of the ven object."""


@final
class NewVen(Ven[None], CreationGuarded):
    """Class representing a new ven not yet pushed to the VTN."""


@final
class VenUpdate(BaseModel):
    """Class representing an update to a ven."""

    ven_name: str | None = Field(default=None, min_length=1, max_length=128)
    """The ven name of the ven object."""

    attributes: tuple[Attribute, ...] | None = None
    """The attributes of the ven."""

    targets: tuple[Target, ...] | None = None
    """The targets of the ven object."""

    resources: tuple[ExistingResource, ...] | None = None
    """The resources of the ven object."""


@final
class ExistingVen(Ven[str]):
    """Class representing an existing ven retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    def update(self, update: VenUpdate) -> "ExistingVen":
        """
        Update the existing ven with the provided update.

        Args:
            update (VenUpdate): The update to apply to the ven.

        Returns:
            ExistingVen: The updated ven.

        """
        current_ven = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_ven = current_ven | update_dict
        return ExistingVen(**updated_ven)
