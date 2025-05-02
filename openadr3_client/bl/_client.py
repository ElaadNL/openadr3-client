from typing import final

from openadr3_client._vtn.interfaces.events import ReadWriteEventsInterface
from openadr3_client._vtn.interfaces.programs import ReadWriteProgramsInterface
from openadr3_client._vtn.interfaces.reports import ReadOnlyReportsInterface
from openadr3_client._vtn.interfaces.subscriptions import ReadOnlySubscriptionsInterface
from openadr3_client._vtn.interfaces.vens import ReadOnlyVensInterface


@final
class BusinessLogicClient:
    """
    Represents the OpenADR 3.0 business logic client.

    The business logic clients communicates with the VTN.
    """

    def __init__(
        self,
        events: ReadWriteEventsInterface,
        programs: ReadWriteProgramsInterface,
        reports: ReadOnlyReportsInterface,
        vens: ReadOnlyVensInterface,
        subscriptions: ReadOnlySubscriptionsInterface,
    ) -> None:
        """
        Initializes the business logic client.

        Args:
            events (ReadWriteEventsInterface): The events interface.
            programs (ReadWriteProgramsInterface): The programs interface.
            reports (ReadOnlyReportsInterface): The reports interface.
            vens (ReadOnlyVensInterface): The VENs interface.
            subscriptions (ReadOnlySubscriptionsInterface): The subscriptions interface.

        """
        self._events = events
        self._programs = programs
        self._reports = reports
        self._vens = vens
        self._subscriptions = subscriptions

    @property
    def events(self) -> ReadWriteEventsInterface:
        return self._events

    @property
    def programs(self) -> ReadWriteProgramsInterface:
        return self._programs

    @property
    def reports(self) -> ReadOnlyReportsInterface:
        return self._reports

    @property
    def vens(self) -> ReadOnlyVensInterface:
        return self._vens

    @property
    def subscriptions(self) -> ReadOnlySubscriptionsInterface:
        return self._subscriptions
