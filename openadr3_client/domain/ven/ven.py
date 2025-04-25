from abc import ABC
from contextlib import contextmanager
from threading import Lock
from typing import Iterator, Tuple

from pydantic import AwareDatetime, Field, PrivateAttr, field_validator
from openadr3_client.domain.common.attribute import Attribute
from openadr3_client.domain.common.target import Target
from openadr3_client.domain.model import ValidatableModel
from openadr3_client.domain.ven.resource import ExistingResource

class Ven[T](ABC, ValidatableModel):
    """Base class for vens."""

    id: T
    """The identifier for the report."""

    ven_name: str = Field(min_length=1, max_length=128)
    """The ven name of the ven object."""

    attributes: Tuple[Attribute, ...] | None = None
    """The attributes of the ven."""

    targets: Tuple[Target, ...] | None = None
    """The targets of the ven object."""

    resources: Tuple[ExistingResource, ...] | None = None
    """The resources of the ven object."""


class NewVen(Ven[None]):
    """Class representing a new ven not yet pushed to the VTN."""

    """Private flag to track if NewVen has been used to create a ven in the VTN.

    If this flag is set to true, calls to create a ven inside the VTN with
    this NewVen object will be rejected."""
    _created: bool = PrivateAttr(default=False)

    """Lock object to synchronize access to with_creation_guard."""
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @contextmanager
    def with_creation_guard(self) -> Iterator[None]:
        """
        A guard which enforces that a NewVen can only be used once.

        A NewVen can only be used to create a ven inside a VTN exactly once.
        Subsequent calls to create the NewVen with the same object will raise an
        exception.

        Raises:
            ValueError: Raised if the NewVen has already been created inside the VTN.

        """
        with self._lock:
            if self._created:
                err_msg = "NewVen has already been created."
                raise ValueError(err_msg)

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise


class ExistingVen(Ven[str]):
    """Class representing an existing ven retrieved from the VTN."""

    created_date_time: AwareDatetime
    modification_date_time: AwareDatetime
