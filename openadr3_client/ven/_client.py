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
        self.events = events
        self.programs = programs
        self.reports = reports
        self.vens = vens
        self.subscriptions = subscriptions
