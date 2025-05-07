from collections.abc import Iterator
from contextlib import contextmanager
from threading import Lock

from pydantic import PrivateAttr

from openadr3_client.models.model import ValidatableModel


class CreationGuarded(ValidatableModel):
    """
    A class which implements a commonly used creation guard pattern.

    The creation guard pattern is used to ensure that certain models can only be used to create OpenADR3 resources
    in a VTN exactly once.
    """

    """Private flag to track if this object has been used to create a program in the VTN.

    If this flag is set to true, calls to create a resource inside the VTN with
    this object will be rejected."""
    _created: bool = PrivateAttr(default=False)

    """Lock object to synchronize access to with_creation_guard."""
    _lock: Lock = PrivateAttr(default_factory=Lock)

    @contextmanager
    def with_creation_guard(self) -> Iterator[None]:
        """
        A guard which enforces that a CreationGuarded object can only be used once.

        A CreationGuarded can only be used to create a resource inside a VTN exactly once.
        Subsequent calls to create the resource with the same object will raise an
        exception.

        Raises:
            ValueError: Raised if the CreationGuarded has already been created inside the VTN.

        """
        with self._lock:
            if self._created:
                err_msg = "CreationGuarded object has already been created."
                raise ValueError(err_msg)

            self._created = True
            try:
                yield
            except Exception:
                self._created = False
                raise
