from abc import ABC
from typing import Literal, final

from pydantic import AwareDatetime, Field

from openadr3_client._models._base_model import BaseModel
from openadr3_client._models._validatable_model import OpenADRResource
from openadr3_client.oadr310.models.common.attribute import Attribute
from openadr3_client.oadr310.models.common.creation_guarded import CreationGuarded


class Resource(ABC, OpenADRResource):
    """Class representing a resource, which is subject to control by a ven."""

    resource_name: str = Field(min_length=1, max_length=128)
    """The name of the resource."""

    ven_id: str = Field(alias="venID", min_length=1, max_length=128)
    """The identifier of the ven this resource belongs to."""

    attributes: tuple[Attribute, ...] | None = None
    """The attributes of the resource."""

    @property
    def name(self) -> str:
        """Helper method to get the name field of the model."""
        return self.resource_name


class NewResource(Resource, CreationGuarded, ABC):
    """Class representing a new resource not yet pushed to the VTN."""


@final
class NewResourceVenRequest(NewResource):
    """Class representing a new resource not yet pushed to the VTN by a VEN client."""

    object_type: Literal["VEN_RESOURCE_REQUEST"] = Field(default="VEN_RESOURCE_REQUEST")
    """The object type."""


@final
class NewResourceBlRequest(NewResource):
    """Class representing a new resource not yet pushed to the VTN by a BL client."""

    object_type: Literal["BL_RESOURCE_REQUEST"] = Field(default="BL_RESOURCE_REQUEST")
    """The object type."""

    client_id: str = Field(alias="clientID", min_length=1, max_length=128)
    """Client ID of the VEN associated with the resource.

    MUST be assigned by a BL client, a VTN will reject or ignore the client ID provided by a VEN client.
    """

    targets: tuple[str, ...] | None = None
    """The targets of the resource.

    Can only be assigned by a BL client, a VTN will reject or ignore targets provided by a VEN client."""


class ResourceUpdate(ABC, BaseModel):
    """Class representing an update to a resource."""

    resource_name: str | None = Field(default=None, min_length=1, max_length=128)
    """The name of the resource."""

    ven_id: str | None = Field(alias="venID", default=None, min_length=1, max_length=128)
    """The identifier of the ven this resource belongs to."""

    attributes: tuple[Attribute, ...] | None = None
    """The attributes of the resource."""


@final
class ResourceUpdateVenRequest(ResourceUpdate):
    """Class representing an update to a resource by a VEN client."""

    object_type: Literal["VEN_RESOURCE_REQUEST"] = Field(default="VEN_RESOURCE_REQUEST")
    """The object type."""


@final
class ResourceUpdateBlRequest(ResourceUpdate):
    """Class representing an update to a resource by a BL client."""

    object_type: Literal["BL_RESOURCE_REQUEST"] = Field(default="BL_RESOURCE_REQUEST")
    """The object type."""

    client_id: str = Field(alias="clientID", min_length=1, max_length=128)
    """Client ID of the VEN associated with the resource.

    MUST be assigned by a BL client, a VTN will reject or ignore the client ID provided by a VEN client.
    """

    targets: tuple[str, ...] | None = None
    """The targets of the resource.

    Can only be assigned by a BL client, a VTN will reject or ignore targets provided by a VEN client."""


class ServerResource(Resource):
    """Class representing an existing report retrieved from the VTN."""

    id: str
    """Identifier of the resource."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    client_id: str = Field(alias="clientID", min_length=1, max_length=128)
    """Client ID of the VEN associated with the resource.

    MUST be assigned by a BL client, a VTN will reject or ignore the client ID provided by a VEN client.
    """

    targets: tuple[str, ...] | None = None
    """The targets of the resource.

    Can only be assigned by a BL client, a VTN will reject or ignore targets provided by a VEN client."""


@final
class ExistingResource(ServerResource):
    """Class representing an existing resource retrieved from the VTN."""

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


@final
class DeletedResource(ServerResource):
    """Class representing a deleted resource retrieved from the VTN."""
