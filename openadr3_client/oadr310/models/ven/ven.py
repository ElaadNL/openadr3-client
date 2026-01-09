from abc import ABC
from typing import Literal, final

from pydantic import AwareDatetime, Field

from openadr3_client._models._base_model import BaseModel
from openadr3_client._models._validatable_model import OpenADRResource
from openadr3_client._models.common.attribute import Attribute
from openadr3_client._models.common.creation_guarded import CreationGuarded


class _VenBase(BaseModel):
    """Base class containing common properties for Ven and VenUpdate."""

    ven_name: str = Field(min_length=1, max_length=128)
    """The ven name of the ven object."""

    attributes: tuple[Attribute, ...] | None = None
    """The attributes of the ven."""


class Ven(ABC, OpenADRResource, _VenBase):
    """Base class for vens."""

    @property
    def name(self) -> str | None:
        """Helper method to get the name field of the model."""
        return self.ven_name


class NewVen(Ven, CreationGuarded):
    """Base class representing a new VEN that was not yet pushed to the VTN."""


@final
class NewVenVenRequest(NewVen):
    """Class representing a new ven created by a VEN not yet pushed to the VTN."""

    object_type: Literal["VEN_VEN_REQUEST"] = Field(default="VEN_VEN_REQUEST")
    """The object type."""


@final
class NewVenBlRequest(NewVen):
    """Class representing a new ven created by a BL not yet pushed to the VTN."""

    targets: tuple[str, ...] | None = None
    """The targets of the ven object.

    Can only be assigned by a BL client, a VTN will reject or ignore targets provided by a VEN client.
    """

    client_id: str = Field(alias="clientID", min_length=1, max_length=128)
    """Client ID of the VEN.

    MUST be assigned by a BL client, a VTN will reject or ignore the client ID provided by a VEN client.
    """

    object_type: Literal["BL_VEN_REQUEST"] = Field(default="BL_VEN_REQUEST")
    """The object type."""


class VenUpdate(ABC, _VenBase):
    """Class representing an update to a ven by a VEN client."""


@final
class VenUpdateVenRequest(VenUpdate):
    """Class representing an update to a ven by a VEN client."""

    object_type: Literal["VEN_VEN_REQUEST"] = Field(default="VEN_VEN_REQUEST")
    """The object type."""


@final
class VenUpdateBlRequest(VenUpdate):
    """Class representing an update to a ven by a BL client."""

    targets: tuple[str, ...] | None = None
    """The targets of the ven object.

    Can only be assigned by a BL client, a VTN will reject or ignore targets provided by a VEN client."""

    client_id: str = Field(alias="clientID", min_length=1, max_length=128)
    """Client ID of the VEN.

    MUST be assigned by a BL client, a VTN will reject or ignore the client ID provided by a VEN client.
    """

    object_type: Literal["BL_VEN_REQUEST"] = Field(default="BL_VEN_REQUEST")
    """The object type."""


class ServerVen(Ven):
    """Class representing a ven retrieved from the VTN."""

    id: str
    """The identifier of the ven object."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    targets: tuple[str, ...] | None = None
    """The targets of the ven object.

    Can only be assigned by a BL client, a VTN will reject or ignore targets provided by a VEN client.
    """

    client_id: str = Field(alias="clientID", min_length=1, max_length=128)
    """Client ID of the VEN.

    MUST be assigned by a BL client, a VTN will reject or ignore the client ID provided by a VEN client.
    """


@final
class ExistingVen(ServerVen):
    """Class representing an existing ven retrieved from the VTN."""

    def update(self, update: VenUpdate) -> "ExistingVen":
        """
        Update the existing ven with the provided update.

        Args:
            update: The update to apply to the ven.

        Returns:
            The updated ven.

        """
        current_ven = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_ven = current_ven | update_dict
        return ExistingVen(**updated_ven)


@final
class DeletedVen(ServerVen):
    """Class representing a deleted ven."""
