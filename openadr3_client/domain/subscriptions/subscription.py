from abc import ABC
from contextlib import contextmanager
from enum import Enum
from threading import Lock
from typing import Iterator, Optional, Tuple, final

from pydantic import AwareDatetime, Field, PrivateAttr, HttpUrl, field_validator
from openadr3_client.domain.common.target import Target
from openadr3_client.domain.model import ValidatableModel

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
class ObjectOperation:
    """Represents a single object operation."""
    objects: Tuple[Object, ...]
    """The objects that trigger this operation."""

    operations: Tuple[Operation, ...]
    """The operations that trigger this operation."""

    callback_url: HttpUrl
    """Callback URL for the operation."""

    bearer_token: Optional[str]
    """User provided bearer token.
    
    To avoid custom integrations, callback endpoints should accept the provided bearer token to authenticate VTN requests.
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

    object_operations: Tuple[ObjectOperation, ...]
    """The object operations of the subscription object."""

    targets: Tuple[Target, ...] | None = None
    """The targets of the subscription object."""

    @field_validator("object_operations", mode="after")
    @classmethod
    def atleast_one_object_operation(cls, object_operations: tuple[ObjectOperation, ...]) -> tuple[ObjectOperation, ...]:
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
class NewSubscription(Subscription[None]):
    """Class representing a new subscription not yet pushed to the VTN."""

    """Private flag to track if NewSubscription has been used to create a subscription in the VTN.

    If this flag is set to true, calls to create a subscription inside the VTN with
    this NewSubscription object will be rejected."""
    _created: bool = PrivateAttr(default=False)

    """Lock object to synchronize access to with_creation_guard."""
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @contextmanager
    def with_creation_guard(self) -> Iterator[None]:
        """
        A guard which enforces that a NewSubscription can only be used once.

        A NewSubscription can only be used to create a subscription inside a VTN exactly once.
        Subsequent calls to create the NewSubscription with the same object will raise an
        exception.

        Raises:
            ValueError: Raised if the NewSubscription has already been created inside the VTN.

        """
        with self._lock:
            if self._created:
                err_msg = "NewSubscription has already been created."
                raise ValueError(err_msg)

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise

@final
class ExistingSubscription(Subscription[str]):
    """Class representing an existing subscription retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime
