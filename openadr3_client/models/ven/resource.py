from abc import ABC
from collections.abc import Iterator
from contextlib import contextmanager
from threading import Lock
from typing import final

from pydantic import AwareDatetime, Field, PrivateAttr

from openadr3_client.models.common.attribute import Attribute
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
class NewResource(Resource[None]):
    """Class representing a new resource not yet pushed to the VTN."""

    """Private flag to track if NewResource has been used to create a resource in the VTN.

    If this flag is set to true, calls to create a resource inside the VTN with
    this NewResource object will be rejected."""
    _created: bool = PrivateAttr(default=False)

    """Lock object to synchronize access to with_creation_guard."""
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @contextmanager
    def with_creation_guard(self) -> Iterator[None]:
        """
        A guard which enforces that a NewResource can only be used once.

        A NewResource can only be used to create a resource inside a VTN exactly once.
        Subsequent calls to create the NewResource with the same object will raise an
        exception.

        Raises:
            ValueError: Raised if the NewResource has already been created inside the VTN.

        """
        with self._lock:
            if self._created:
                err_msg = "NewResource has already been created."
                raise ValueError(err_msg)

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise


@final
class ExistingResource(Resource[str]):
    """Class representing an existing report retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime
