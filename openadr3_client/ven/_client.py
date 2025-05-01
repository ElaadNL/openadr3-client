from typing import final

from openadr3_client._vtn.interfaces.events import ReadOnlyEventsInterface
from openadr3_client._vtn.interfaces.programs import ReadOnlyProgramsInterface
from openadr3_client._vtn.interfaces.reports import ReadWriteReportsInterface
from openadr3_client._vtn.interfaces.subscriptions import ReadWriteSubscriptionsInterface
from openadr3_client._vtn.interfaces.vens import ReadWriteVensInterface


@final
class VirtualEndNodeClient:
    """
    Represents the OpenADR 3.0 virtual end node (VEN) client.

    The VEN client communicates with the VTN.
    """

    def __init__(
        self,
        events: ReadOnlyEventsInterface,
        programs: ReadOnlyProgramsInterface,
        reports: ReadWriteReportsInterface,
        vens: ReadWriteVensInterface,
        subscriptions: ReadWriteSubscriptionsInterface,
    ) -> None:
        """
        Initializes the VEN client.

        Args:
            events (ReadOnlyEventsInterface): The events interface.
            programs (ReadOnlyProgramsInterface): The programs interface.
            reports (ReadWriteReportsInterface): The reports interface.
            vens (ReadWriteVensInterface): The VENs interface.
            subscriptions (ReadWriteSubscriptionsInterface): The subscriptions interface.

        """
        self._events = events
        self._programs = programs
        self._reports = reports
        self._vens = vens
        self._subscriptions = subscriptions

    @property
    def events(self) -> ReadOnlyEventsInterface:
        return self._events

    @property
    def programs(self) -> ReadOnlyProgramsInterface:
        return self._programs

    @property
    def reports(self) -> ReadWriteReportsInterface:
        return self._reports

    @property
    def vens(self) -> ReadWriteVensInterface:
        return self._vens

    @property
    def subscriptions(self) -> ReadWriteSubscriptionsInterface:
        return self._subscriptions
