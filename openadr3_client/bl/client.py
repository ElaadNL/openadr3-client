from openadr3_client.vtn._events import EventsInterface
from openadr3_client.vtn._programs import ProgramsInterface
from openadr3_client.vtn._reports import ReportsReadOnlyInterface
from openadr3_client.vtn._subscriptions import SubscriptionsReadOnlyInterface
from openadr3_client.vtn._vens import VensReadOnlyInterface


class BusinessLogicClient:
    """Represents the OpenADR 3.0 business logic client.

    The business logic client allows for the following actions within OpenADR3:

    - Create, read, update and delete events.
    - Create, read, update and delete programs.
    - Read all OpenADR3 resources.
    """
    def __init__(self):
        """Initializes the business logic client."""
        self.events = EventsInterface()
        self.programs = ProgramsInterface()
        self.reports = ReportsReadOnlyInterface()
        self.vens = VensReadOnlyInterface()
        self.subscriptions = SubscriptionsReadOnlyInterface()