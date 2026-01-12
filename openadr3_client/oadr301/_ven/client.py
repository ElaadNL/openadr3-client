from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.oadr301._vtn.http.events import EventsReadOnlyHttpInterface
from openadr3_client.oadr301._vtn.http.programs import ProgramsReadOnlyHttpInterface
from openadr3_client.oadr301._vtn.http.reports import ReportsHttpInterface
from openadr3_client.oadr301._vtn.http.subscriptions import SubscriptionsHttpInterface
from openadr3_client.oadr301._vtn.http.vens import VensHttpInterface
from openadr3_client.oadr301._vtn.interfaces.events import ReadOnlyEventsInterface
from openadr3_client.oadr301._vtn.interfaces.programs import ReadOnlyProgramsInterface
from openadr3_client.oadr301._vtn.interfaces.reports import ReadWriteReportsInterface
from openadr3_client.oadr301._vtn.interfaces.subscriptions import ReadOnlySubscriptionsInterface
from openadr3_client.oadr301._vtn.interfaces.vens import ReadWriteVensInterface
from openadr3_client.ven._client import BaseVirtualEndNodeClient
from openadr3_client.version import OADRVersion


@final
class VirtualEndNodeClient(BaseVirtualEndNodeClient):
    """
    Represents the OpenADR 3.0.1 virtual end node client.

    The virtual end node client communicates with the VTN.
    """

    def __init__(
        self,
        version: OADRVersion,
        events: ReadOnlyEventsInterface,
        programs: ReadOnlyProgramsInterface,
        reports: ReadWriteReportsInterface,
        vens: ReadWriteVensInterface,
        subscriptions: ReadOnlySubscriptionsInterface,
    ) -> None:
        """
        Initializes the business logic client.

        Args:
            version (OADRVersion): The OpenADR version used by this client.
            auth (ReadOnlyAuthInterface): The auth interface.
            events (ReadWriteEventsInterface): The events interface.
            programs (ReadWriteProgramsInterface): The programs interface.
            reports (ReadOnlyReportsInterface): The reports interface.
            vens (ReadWriteVensInterface): The VENS interface.
            subscriptions (ReadOnlySubscriptionsInterface): The subscriptions interface.
            notifiers (ReadOnlyNotifierInterface): The notifiers interface.
            resources (ReadWriteResourceInterface): The resources interface.

        """
        super().__init__(version=version)
        self._events = events
        self._programs = programs
        self._reports = reports
        self._vens = vens
        self._subscriptions = subscriptions

    @property
    def events(self) -> ReadOnlyEventsInterface:
        """
        The events BL interface.

        Returns:
            ReadOnlyEventsInterface: The events BL interface.

        """
        return self._events

    @property
    def programs(self) -> ReadOnlyProgramsInterface:
        """
        The programs BL interface.

        Returns:
            ReadOnlyProgramsInterface: The programs BL interface.

        """
        return self._programs

    @property
    def reports(self) -> ReadWriteReportsInterface:
        """
        The reports BL interface.

        Returns:
            ReadWriteReportsInterface: The reports BL interface.

        """
        return self._reports

    @property
    def vens(self) -> ReadWriteVensInterface:
        """
        The vens BL interface.

        Returns:
            ReadWriteVensInterface: The vens BL interface.

        """
        return self._vens

    @property
    def subscriptions(self) -> ReadOnlySubscriptionsInterface:
        """
        The subscriptions BL interface.

        Returns:
            ReadOnlySubscriptionsInterface: The subscriptions BL interface.

        """
        return self._subscriptions


def get_oadr301_ven_client(
    vtn_base_url: str,
    config: OAuthTokenManagerConfig,
) -> VirtualEndNodeClient:
    """
    Creates the OpenADR 3.0.1 virtual end node client.

    Args:
        vtn_base_url (str): The base URL for the HTTP interface of the VTN.
        config (OAuthTokenManagerConfig): The OAuth token manager configuration.

    Returns:
        VirtualEndNodeClient: The virtual end node client instance.

    """
    return VirtualEndNodeClient(
        version=OADRVersion.OADR_301,
        events=EventsReadOnlyHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        programs=ProgramsReadOnlyHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        reports=ReportsHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        vens=VensHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        subscriptions=SubscriptionsHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
    )
