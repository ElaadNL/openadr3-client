from typing import final

from openadr3_client._vtn.http.events import EventsReadOnlyHttpInterface
from openadr3_client._vtn.http.programs import ProgramsReadOnlyHttpInterface
from openadr3_client._vtn.http.reports import ReportsHttpInterface
from openadr3_client._vtn.http.subscriptions import SubscriptionsHttpInterface
from openadr3_client._vtn.http.vens import VensHttpInterface
from openadr3_client.ven._client import VirtualEndNodeClient


@final
class VirtualEndNodeHttpClientFactory:
    """Factory which can be used to create a virtual end node (VEN) http client."""

    @staticmethod
    def create_http_ven_client(vtn_base_url: str) -> VirtualEndNodeClient:
        """
        Creates a VEN client which uses the HTTP interface of a VTN.

        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.

        """
        return VirtualEndNodeClient(
            events=EventsReadOnlyHttpInterface(base_url=vtn_base_url),
            programs=ProgramsReadOnlyHttpInterface(base_url=vtn_base_url),
            reports=ReportsHttpInterface(base_url=vtn_base_url),
            vens=VensHttpInterface(base_url=vtn_base_url),
            subscriptions=SubscriptionsHttpInterface(base_url=vtn_base_url),
        )
