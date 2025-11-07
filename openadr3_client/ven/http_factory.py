from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
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
    def create_http_ven_client(
        vtn_base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        scopes: list[str] | None = None,
        verify_vtn_tls_certificate: bool | str = True,
    ) -> VirtualEndNodeClient:
        """
        Creates a VEN client which uses the HTTP interface of a VTN.

        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.
            client_id (str): The client id to use to provision an access token from the OAuth authorization server.
            client_secret (str): The client secret to use to provision an access token from the OAuth authorization server.
            token_url (str): The endpoint to provision access tokens from.
            scopes (list[str]): The scopes to request with the token. If empty, no scopes are requested.
            verify_vtn_tls_certificate (bool | str): Whether the VEN verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.

        """  # noqa: E501
        config = OAuthTokenManagerConfig(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=None,
        )
        return VirtualEndNodeClient(
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
        )
