# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.oadr310._vtn.http.auth import AuthReadOnlyInterface
from openadr3_client.oadr310._vtn.http.events import EventsReadOnlyHttpInterface
from openadr3_client.oadr310._vtn.http.notifiers import NotifiersReadOnlyHttpInterface
from openadr3_client.oadr310._vtn.http.programs import ProgramsReadOnlyHttpInterface
from openadr3_client.oadr310._vtn.http.reports import ReportsHttpInterface
from openadr3_client.oadr310._vtn.http.resources import ResourcesHttpInterface
from openadr3_client.oadr310._vtn.http.subscriptions import SubscriptionsHttpInterface
from openadr3_client.oadr310._vtn.http.vens import VensHttpInterface
from openadr3_client.oadr310._vtn.interfaces.auth import ReadOnlyAuthInterface
from openadr3_client.oadr310._vtn.interfaces.events import ReadOnlyEventsInterface
from openadr3_client.oadr310._vtn.interfaces.notifiers import ReadOnlyNotifierInterface
from openadr3_client.oadr310._vtn.interfaces.programs import ReadOnlyProgramsInterface
from openadr3_client.oadr310._vtn.interfaces.reports import ReadWriteReportsInterface
from openadr3_client.oadr310._vtn.interfaces.resources import ReadWriteResourceInterface
from openadr3_client.oadr310._vtn.interfaces.subscriptions import ReadOnlySubscriptionsInterface
from openadr3_client.oadr310._vtn.interfaces.vens import ReadWriteVensInterface
from openadr3_client.ven._client import BaseVirtualEndNodeClient
from openadr3_client.version import OADRVersion


@final
class VirtualEndNodeClient(BaseVirtualEndNodeClient):
    """
    Represents the OpenADR 3.1.0 virtual end node client.

    The virtual end node client communicates with the VTN.
    """

    def __init__(
        self,
        version: OADRVersion,
        auth: ReadOnlyAuthInterface,
        events: ReadOnlyEventsInterface,
        programs: ReadOnlyProgramsInterface,
        reports: ReadWriteReportsInterface,
        vens: ReadWriteVensInterface,
        subscriptions: ReadOnlySubscriptionsInterface,
        notifiers: ReadOnlyNotifierInterface,
        resources: ReadWriteResourceInterface,
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
        self._auth = auth
        self._events = events
        self._programs = programs
        self._reports = reports
        self._vens = vens
        self._subscriptions = subscriptions
        self._notifiers = notifiers
        self._resources = resources

    @property
    def auth(self) -> ReadOnlyAuthInterface:
        """
        The auth BL interface.

        Returns:
            ReadOnlyAuthInterface: The auth BL interface.

        """
        return self._auth

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

    @property
    def notifiers(self) -> ReadOnlyNotifierInterface:
        """
        The notifiers BL interface.

        Returns:
            ReadOnlyNotifierInterface: The notifiers BL interface.

        """
        return self._notifiers

    @property
    def resources(self) -> ReadWriteResourceInterface:
        """
        The resources BL interface.

        Returns:
            ReadWriteResourceInterface: The resources BL interface.

        """
        return self._resources


def get_oadr310_ven_client(
    vtn_base_url: str,
    config: OAuthTokenManagerConfig,
    *,
    verify_vtn_tls_certificate: bool | str = True,
) -> VirtualEndNodeClient:
    """
    Creates the OpenADR 3.1.0 virtual end node client.

    Args:
        vtn_base_url (str): The base URL for the HTTP interface of the VTN.
        config (OAuthTokenManagerConfig): The OAuth token manager configuration.
        verify_vtn_tls_certificate (bool | str): Whether the BL verifies the TLS certificate of the VTN.
        Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
        If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
        PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.

    Returns:
        VirtualEndNodeClient: The virtual end node client instance.

    """
    return VirtualEndNodeClient(
        version=OADRVersion.OADR_310,
        auth=AuthReadOnlyInterface(
            base_url=vtn_base_url,
            verify_tls_certificate=verify_vtn_tls_certificate,
        ),
        events=EventsReadOnlyHttpInterface(
            base_url=vtn_base_url,
            config=config,
            verify_tls_certificate=verify_vtn_tls_certificate,
        ),
        programs=ProgramsReadOnlyHttpInterface(
            base_url=vtn_base_url,
            config=config,
            verify_tls_certificate=verify_vtn_tls_certificate,
        ),
        reports=ReportsHttpInterface(
            base_url=vtn_base_url,
            config=config,
            verify_tls_certificate=verify_vtn_tls_certificate,
        ),
        vens=VensHttpInterface(
            base_url=vtn_base_url,
            config=config,
            verify_tls_certificate=verify_vtn_tls_certificate,
        ),
        subscriptions=SubscriptionsHttpInterface(
            base_url=vtn_base_url,
            config=config,
            verify_tls_certificate=verify_vtn_tls_certificate,
        ),
        notifiers=NotifiersReadOnlyHttpInterface(base_url=vtn_base_url, config=config, verify_tls_certificate=verify_vtn_tls_certificate),
        resources=ResourcesHttpInterface(base_url=vtn_base_url, config=config, verify_tls_certificate=verify_vtn_tls_certificate),
    )
