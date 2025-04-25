from typing import final
from openadr3_client.vtn._events import EventsInterface
from openadr3_client.vtn._programs import ProgramsInterface
from openadr3_client.vtn._reports import ReportsReadOnlyInterface
from openadr3_client.vtn._subscriptions import SubscriptionsReadOnlyInterface
from openadr3_client.vtn._vens import VensReadOnlyInterface

@final
class BusinessLogicClient:
    """Represents the OpenADR 3.0 business logic client.

    The business logic client allows for the following actions within OpenADR3:

    - Create, read, update and delete events.
    - Create, read, update and delete programs.
    - Read all OpenADR3 resources.
    """
    def __init__(self, vtn_base_url: str) -> None:
        """Initializes the business logic client.
        
        Args:
            vtn_base_url (str): The base URL of the OpenADR 3.0 VTN.
        """
        self.events = EventsInterface(base_url=vtn_base_url)
        self.programs = ProgramsInterface(base_url=vtn_base_url)
        self.reports = ReportsReadOnlyInterface(base_url=vtn_base_url)
        self.vens = VensReadOnlyInterface(base_url=vtn_base_url)
        self.subscriptions = SubscriptionsReadOnlyInterface(base_url=vtn_base_url)