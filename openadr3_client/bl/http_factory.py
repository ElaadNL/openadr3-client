from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client._vtn.http.auth import AuthReadOnlyInterface
from openadr3_client._vtn.http.events import EventsHttpInterface
from openadr3_client._vtn.http.programs import ProgramsHttpInterface
from openadr3_client._vtn.http.reports import ReportsReadOnlyHttpInterface
from openadr3_client._vtn.http.subscriptions import SubscriptionsReadOnlyHttpInterface
from openadr3_client._vtn.http.vens import VensHttpInterface
from openadr3_client.bl._client import BusinessLogicClient
from openadr3_client.logging import logger


@final
class BusinessLogicHttpClientFactory:
    """Factory which can be used to create a business logic http client."""

    @staticmethod
    def create_http_bl_client(
        vtn_base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str | None = None,
        scopes: list[str] | None = None,
        audience: str | None = None,
        *,
        verify_vtn_tls_certificate: bool | str = True,
    ) -> BusinessLogicClient:
        """
        Creates a business logic client which uses the HTTP interface of a VTN.

        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.
            client_id (str): The client id to use to provision an access token from the OAuth authorization server.
            client_secret (str): The client secret to use to provision an access token from the OAuth authorization server.
            token_url (str | None): The endpoint to provision access tokens from. Defaults to None. If None, the token URL is discovered by calling
            the discover endpoint (introduced in OpenADR 3.1) on the OpenADR VTN.
            scopes (list[str]): The scopes to request with the token. If empty, no scopes are requested.
            audience (str): The audience to request with the token. If empty, no audience is requested.
            verify_vtn_tls_certificate (bool | str): Whether the BL verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.

        """
        # TODO: Likely not the best place to do this, but works for the # noqa: FIX002, TD003, TD002
        # initial migration steps. Reconsider and clean up when all changes are implemented.
        if token_url is None:
            # If token URL is None, discover the token URL from the VTN through the discovery endpoint.
            logger.info("Token URL not provided to VEN client factory, calling VTN discovery endpoint to fetch token URL...")
            auth_interface = AuthReadOnlyInterface(base_url=vtn_base_url, verify_tls_certificate=verify_vtn_tls_certificate)
            auth_server_info = auth_interface.get_auth_server()
            token_url = auth_server_info.token_url

        config = OAuthTokenManagerConfig(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=audience,
        )

        return BusinessLogicClient(
            events=EventsHttpInterface(
                base_url=vtn_base_url,
                config=config,
                verify_tls_certificate=verify_vtn_tls_certificate,
            ),
            programs=ProgramsHttpInterface(
                base_url=vtn_base_url,
                config=config,
                verify_tls_certificate=verify_vtn_tls_certificate,
            ),
            reports=ReportsReadOnlyHttpInterface(
                base_url=vtn_base_url,
                config=config,
                verify_tls_certificate=verify_vtn_tls_certificate,
            ),
            vens=VensHttpInterface(
                base_url=vtn_base_url,
                config=config,
                verify_tls_certificate=verify_vtn_tls_certificate,
            ),
            subscriptions=SubscriptionsReadOnlyHttpInterface(
                base_url=vtn_base_url,
                config=config,
                verify_tls_certificate=verify_vtn_tls_certificate,
            ),
        )
