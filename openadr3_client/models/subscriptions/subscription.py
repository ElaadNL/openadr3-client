from abc import ABC
from enum import Enum
from typing import final

from pydantic import AwareDatetime, Field, HttpUrl, field_validator

from openadr3_client.models._base_model import BaseModel
from openadr3_client.models.common.creation_guarded import CreationGuarded
from openadr3_client.models.common.target import Target
from openadr3_client.models.model import ValidatableModel


@final
class Object(str, Enum):
    """Enumeration of the object types of OpenADR 3."""

    PROGRAM = "PROGRAM"
    EVENT = "EVENT"
    REPORT = "REPORT"
    SUBSCRIPTION = "SUBSCRIPTION"
    VEN = "VEN"
    RESOURCE = "RESOURCE"


@final
class Operation(str, Enum):
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
            objects (tuple[Object, ...]): The objects of the object operation.

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
            operations (tuple[Operation, ...]): The operations of the object operation.

        """
        if len(operations) == 0:
            err_msg = "ObjectOperation must contain at least one operation."
            raise ValueError(err_msg)
        return operations


class Subscription[T](ABC, ValidatableModel):
    """Base class for subscription objects."""

    id: T
    """The identifier of the subscription object."""

    client_name: str = Field(min_length=1, max_length=128)
    """The client name of the subscription object."""

    program_id: str = Field(alias="programID", min_length=1, max_length=128)
    """The program id of the subscription object."""

    object_operations: tuple[ObjectOperation, ...]
    """The object operations of the subscription object."""

    targets: tuple[Target, ...] | None = None
    """The targets of the subscription object."""

    @field_validator("object_operations", mode="after")
    @classmethod
    def atleast_one_object_operation(
        cls, object_operations: tuple[ObjectOperation, ...]
    ) -> tuple[ObjectOperation, ...]:
        """
        Validates that a subscription has atleast one object operation defined.

        Args:
            object_operations (tuple[ObjectOperation, ...]): The object operations of the subscription.

        """
        if len(object_operations) == 0:
            err_msg = "Subscription must contain at least one resource."
            raise ValueError(err_msg)
        return object_operations


@final
class NewSubscription(Subscription[None], CreationGuarded):
    """Class representing a new subscription not yet pushed to the VTN."""


@final
class SubscriptionUpdate(BaseModel):
    """Class representing an update to a subscription."""

    client_name: str | None = Field(default=None, min_length=1, max_length=128)
    """The client name of the subscription update."""

    program_id: str | None = Field(alias="programID", default=None, min_length=1, max_length=128)
    """The program id of the subscription update."""

    object_operations: tuple[ObjectOperation, ...] | None = None
    """The object operations of the subscription update."""

    targets: tuple[Target, ...] | None = None
    """The targets of the subscription update."""


@final
class ExistingSubscription(Subscription[str]):
    """Class representing an existing subscription retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime

    def update(self, update: SubscriptionUpdate) -> "ExistingSubscription":
        """
        Update the existing subscription with the provided update.

        Args:
            update (SubscriptionUpdate): The update to apply to the subscription.

        Returns:
            ExistingSubscription: The updated subscription.

        """
        current_subscription = self.model_dump()
        update_dict = update.model_dump(exclude_unset=True)
        updated_subscription = current_subscription | update_dict
        return ExistingSubscription(**updated_subscription)
