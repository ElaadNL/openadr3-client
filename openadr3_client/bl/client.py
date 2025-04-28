from typing import final

from openadr3_client.vtn.common.events import ReadWriteEventsInterface
from openadr3_client.vtn.common.programs import ReadWriteProgramsInterface
from openadr3_client.vtn.common.reports import ReadOnlyReportsInterface
from openadr3_client.vtn.common.subscriptions import ReadOnlySubscriptionsInterface
from openadr3_client.vtn.common.vens import ReadOnlyVensInterface


@final
class BusinessLogicClient:
    """
    Represents the OpenADR 3.0 business logic client.

    The business logic clients communicates with the VTN.
    """

    def __init__(self,
                 events: ReadWriteEventsInterface,
                 programs: ReadWriteProgramsInterface,
                 reports: ReadOnlyReportsInterface,
                 vens: ReadOnlyVensInterface,
                 subscriptions: ReadOnlySubscriptionsInterface) -> None:
        """
        Initializes the business logic client.

        Args:
            events (ReadWriteEventsInterface): The events interface.
            programs (ReadWriteProgramsInterface): The programs interface.
            reports (ReadOnlyReportsInterface): The reports interface.
            vens (ReadOnlyVensInterface): The VENs interface.
            subscriptions (ReadOnlySubscriptionsInterface): The subscriptions interface.
        """
        self.events = events
        self.programs = programs
        self.reports = reports
        self.vens = vens
        self.subscriptions = subscriptions
    

