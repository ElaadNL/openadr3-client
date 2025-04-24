from openadr3_client.vtn._events import EventsInterface
from openadr3_client.vtn._programs import ProgramsInterface
from openadr3_client.vtn._reports import ReportsReadOnlyInterface


class BusinessLogicClient:
    """Represents the OpenADR 3.0 business logic client.

    The business logic client allows for the following actions within OpenADR3:

    - Create, read, update and delete events.
    - Create, read, update and delete programs.
    - Read all OpenADR3 resources.
    """
    def __init__(self):
        """Initializes the business logic client with the given base URL.

        Args:
            base_url (str): The base URL of the OpenADR 3.0 server.
        """
        self.events = EventsInterface()
        self.programs = ProgramsInterface()
        self.reports = ReportsReadOnlyInterface()
        # TODO: READ ONLY INTERFACES OF OTHER RESOURCES.