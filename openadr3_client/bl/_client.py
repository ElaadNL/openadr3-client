from typing import final

from openadr3_client._vtn.oadr310.interfaces.events import ReadWriteEventsInterface
from openadr3_client._vtn.oadr310.interfaces.notifiers import ReadOnlyNotifierInterface
from openadr3_client._vtn.oadr310.interfaces.programs import ReadWriteProgramsInterface
from openadr3_client._vtn.oadr310.interfaces.reports import ReadOnlyReportsInterface
from openadr3_client._vtn.oadr310.interfaces.resources import ReadWriteResourceInterface
from openadr3_client._vtn.oadr310.interfaces.subscriptions import ReadOnlySubscriptionsInterface
from openadr3_client._vtn.oadr310.interfaces.vens import ReadWriteVensInterface


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
        vens: ReadWriteVensInterface,
        subscriptions: ReadOnlySubscriptionsInterface,
        notifiers: ReadOnlyNotifierInterface,
        resources: ReadWriteResourceInterface,
    ) -> None:
        """
        Initializes the business logic client.

        Args:
            events (ReadWriteEventsInterface): The events interface.
            programs (ReadWriteProgramsInterface): The programs interface.
            reports (ReadOnlyReportsInterface): The reports interface.
            vens (ReadOnlyVensInterface): The VENs interface.
            subscriptions (ReadOnlySubscriptionsInterface): The subscriptions interface.
            notifiers (ReadOnlyNotifierInterface): The notifier interface.
            resources (ReadWriteEventsInterface): The resources interface.

        """
        self._events = events
        self._programs = programs
        self._reports = reports
        self._vens = vens
        self._subscriptions = subscriptions
        self._notifiers = notifiers
        self._resources = resources

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
    def vens(self) -> ReadWriteVensInterface:
        return self._vens

    @property
    def subscriptions(self) -> ReadOnlySubscriptionsInterface:
        return self._subscriptions

    @property
    def notifiers(self) -> ReadOnlyNotifierInterface:
        return self._notifiers

    @property
    def resources(self) -> ReadWriteResourceInterface:
        return self._resources
