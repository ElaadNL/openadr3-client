
from typing import final

from openadr3_client.bl._client import BusinessLogicClient
from openadr3_client._vtn.http.events import EventsHttpInterface
from openadr3_client._vtn.http.programs import ProgramsHttpInterface
from openadr3_client._vtn.http.reports import ReportsReadOnlyHttpInterface
from openadr3_client._vtn.http.vens import VensReadOnlyHttpInterface
from openadr3_client._vtn.http.subscriptions import SubscriptionsReadOnlyHttpInterface

@final
class BusinessLogicClientFactory:
    @staticmethod
    def http_bl_client(vtn_base_url: str) -> BusinessLogicClient:
        """Creates a business logic client which uses the HTTP interface of a VTN.
        
        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.
        """
        return BusinessLogicClient(
            events=EventsHttpInterface(base_url=vtn_base_url),
            programs=ProgramsHttpInterface(base_url=vtn_base_url),
            reports=ReportsReadOnlyHttpInterface(base_url=vtn_base_url),
            vens=VensReadOnlyHttpInterface(base_url=vtn_base_url),
            subscriptions=SubscriptionsReadOnlyHttpInterface(base_url=vtn_base_url))