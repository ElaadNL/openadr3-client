from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.bl._client import BaseBusinessLogicClient
from openadr3_client.oadr301._vtn.http.events import EventsHttpInterface
from openadr3_client.oadr301._vtn.http.programs import ProgramsHttpInterface
from openadr3_client.oadr301._vtn.http.reports import ReportsReadOnlyHttpInterface
from openadr3_client.oadr301._vtn.http.subscriptions import SubscriptionsReadOnlyHttpInterface
from openadr3_client.oadr301._vtn.http.vens import VensHttpInterface
from openadr3_client.oadr301._vtn.interfaces.events import ReadWriteEventsInterface
from openadr3_client.oadr301._vtn.interfaces.programs import ReadWriteProgramsInterface
from openadr3_client.oadr301._vtn.interfaces.reports import ReadOnlyReportsInterface
from openadr3_client.oadr301._vtn.interfaces.subscriptions import ReadOnlySubscriptionsInterface
from openadr3_client.oadr301._vtn.interfaces.vens import ReadWriteVensInterface
from openadr3_client.version import OADRVersion


@final
class BusinessLogicClient(BaseBusinessLogicClient):
    """
    Represents the OpenADR 3.0.1 business logic client.

    The business logic clients communicates with the VTN.
    """

    def __init__(
        self,
        version: OADRVersion,
        events: ReadWriteEventsInterface,
        programs: ReadWriteProgramsInterface,
        reports: ReadOnlyReportsInterface,
        vens: ReadWriteVensInterface,
        subscriptions: ReadOnlySubscriptionsInterface,
    ) -> None:
        """
        Initializes the business logic client.

        Args:
            version (OADRVersion): The OpenADR version used by this client.
            events (ReadWriteEventsInterface): The events interface.
            programs (ReadWriteProgramsInterface): The programs interface.
            reports (ReadOnlyReportsInterface): The reports interface.
            vens (ReadWriteVensInterface): The VENS interface.
            subscriptions (ReadOnlySubscriptionsInterface): The subscriptions interface.

        """
        super().__init__(version=version)
        self._events = events
        self._programs = programs
        self._reports = reports
        self._vens = vens
        self._subscriptions = subscriptions

    @property
    def events(self) -> ReadWriteEventsInterface:
        """
        The events BL interface.

        Returns:
            ReadWriteEventsInterface: The events BL interface.

        """
        return self._events

    @property
    def programs(self) -> ReadWriteProgramsInterface:
        """
        The programs BL interface.

        Returns:
            ReadWriteProgramsInterface: The programs BL interface.

        """
        return self._programs

    @property
    def reports(self) -> ReadOnlyReportsInterface:
        """
        The reports BL interface.

        Returns:
            ReadOnlyReportsInterface: The reports BL interface.

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


def get_oadr301_bl_client(
    vtn_base_url: str,
    config: OAuthTokenManagerConfig,
) -> BusinessLogicClient:
    """
    Creates the OpenADR 3.0.1 business logic client.

    Args:
        vtn_base_url (str): The base URL for the HTTP interface of the VTN.
        config (OAuthTokenManagerConfig): The OAuth token manager configuration.

    Returns:
        BusinessLogicClient: The business logic client instance.

    """
    return BusinessLogicClient(
        version=OADRVersion.OADR_301,
        events=EventsHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        programs=ProgramsHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        reports=ReportsReadOnlyHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        vens=VensHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
        subscriptions=SubscriptionsReadOnlyHttpInterface(
            base_url=vtn_base_url,
            config=config,
        ),
    )
