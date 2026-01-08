from abc import ABC
from enum import StrEnum
from typing import final

from pydantic import AwareDatetime, Field, HttpUrl, field_validator

from openadr3_client._models._base_model import BaseModel
from openadr3_client._models._validatable_model import OpenADRResource, ValidatableModel
from openadr3_client.oadr310.models.common.creation_guarded import CreationGuarded


@final
class Object(StrEnum):
    """Enumeration of the object types of OpenADR 3."""

    PROGRAM = "PROGRAM"
    EVENT = "EVENT"
    REPORT = "REPORT"
    SUBSCRIPTION = "SUBSCRIPTION"
    VEN = "VEN"
    RESOURCE = "RESOURCE"


@final
class Operation(StrEnum):
    """Enumeration of the operations of OpenADR 3."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@final
class ObjectOperation(ValidatableModel):
    """Represents a single object operation."""

    objects: tuple[Object, ...]
    """The objects that trigger this operation."""

    operations: tuple[Operation, ...]
    """The operations that trigger this operation."""

    callback_url: HttpUrl
    """Callback URL for the operation."""

    bearer_token: str | None
    """User provided bearer token.

    To avoid custom integrations, callback endpoints should accept
    the provided bearer token to authenticate VTN requests.
    """

    @field_validator("objects", mode="after")
    @classmethod
    def atleast_one_object(cls, objects: tuple[Object, ...]) -> tuple[Object, ...]:
        """
        Validates that an object operation has atleast one object defined.

        Args:
            objects: The objects of the object operation.

        """
        if len(objects) == 0:
            err_msg = "ObjectOperation must contain at least one object."
            raise ValueError(err_msg)
        return objects

    @field_validator("operations", mode="after")
    @classmethod
    def atleast_one_operation(cls, operations: tuple[Operation, ...]) -> tuple[Operation, ...]:
        """
        Validates that an object operation has atleast one operation defined.

        Args:
            operations: The operations of the object operation.

        """
        if len(operations) == 0:
            err_msg = "ObjectOperation must contain at least one operation."
            raise ValueError(err_msg)
        return operations


class _SubscriptionBase(BaseModel):
    """Base class containing common properties for Subscription and SubscriptionUpdate."""

    client_name: str = Field(min_length=1, max_length=128)
    """The client name of the subscription object."""

    program_id: str | None = Field(alias="programID", min_length=1, max_length=128, default=None)
    """The program id of the subscription object."""

    object_operations: tuple[ObjectOperation, ...]
    """The object operations of the subscription object."""

    targets: tuple[str, ...] | None = None
    """The targets of the subscription object."""

    @field_validator("object_operations", mode="after")
    @classmethod
    def atleast_one_object_operation(cls, object_operations: tuple[ObjectOperation, ...]) -> tuple[ObjectOperation, ...]:
        """
        Validates that a subscription has atleast one object operation defined.

        Args:
            object_operations: The object operations of the subscription.

        """
        if len(object_operations) == 0:
            err_msg = "Subscription must contain at least one resource."
            raise ValueError(err_msg)
        return object_operations


class Subscription(ABC, OpenADRResource, _SubscriptionBase):
    """Base class for subscription objects."""

    @property
    def name(self) -> str:
        """Helper method to get the name field of the model."""
        return self.client_name


@final
class NewSubscription(Subscription, CreationGuarded):
    """Class representing a new subscription not yet pushed to the VTN."""


@final
class SubscriptionUpdate(_SubscriptionBase):
    """Class representing an update to a subscription."""


class ServerSubscription(Subscription):
    """Class representing a subscription retrieved from the VTN."""

    id: str
    """The identifier of the subscription object."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime


@final
class ExistingSubscription(ServerSubscription):
    """Class representing an existing subscription retrieved from the VTN."""

    def update(self, update: SubscriptionUpdate) -> "ExistingSubscription":
        """
        Update the existing subscription with the provided update.

        Args:
            update: The update to apply to the subscription.

        Returns:
            The updated subscription.

        """
        current_subscription = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_subscription = current_subscription | update_dict
        return ExistingSubscription(**updated_subscription)


@final
class DeletedSubscription(ServerSubscription):
    """Class representing a deleted subscription."""
