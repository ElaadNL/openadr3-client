from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.logging import logger
from openadr3_client.ven._client import BaseVirtualEndNodeClient
from openadr3_client.version import OADRVersion


@final
class VirtualEndNodeHttpClientFactory:
    """Factory which can be used to create a virtual end node (VEN) http client."""

    @staticmethod
    def create_http_ven_client(
        vtn_base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str | None,
        scopes: list[str] | None = None,
        *,
        verify_vtn_tls_certificate: bool | str = True,
        version: OADRVersion = OADRVersion.OADR_310,
    ) -> BaseVirtualEndNodeClient:
        """
        Creates a VEN client which uses the HTTP interface of a VTN.

        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.
            client_id (str): The client id to use to provision an access token from the OAuth authorization server.
            client_secret (str): The client secret to use to provision an access token from the OAuth authorization server.
            token_url (str | None): The endpoint to provision access tokens from. Defaults to None. If None, the token URL is discovered by calling
            the discover endpoint (introduced in OpenADR 3.1) on the OpenADR VTN.
            scopes (list[str]): The scopes to request with the token. If empty, no scopes are requested.
            verify_vtn_tls_certificate (bool | str): Whether the VEN verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.
            version (OADRVersion): The OpenADR version to use for the VEN client. Defaults to OADR 3.1.0.

        """
        # Starting with OpenADR 3.1.0, the token URL can be discovered from the VTN through the discovery endpoint.
        # This is only done if the token_url has not been manually provided.
        if token_url is None:
            if version == OADRVersion.OADR_301:
                msg = "Token URL must be provided for OpenADR 3.0.1 clients."
                raise ValueError(msg)
            if version == OADRVersion.OADR_310:
                from openadr3_client.oadr310._vtn.http.auth import AuthReadOnlyInterface  # noqa: PLC0415

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
            audience=None,
        )

        if version == OADRVersion.OADR_310:
            from openadr3_client.oadr310._ven.client import get_oadr310_ven_client  # noqa: PLC0415

            return get_oadr310_ven_client(
                vtn_base_url=vtn_base_url,
                config=config,
                verify_vtn_tls_certificate=verify_vtn_tls_certificate,
            )

        from openadr3_client.oadr301._ven.client import get_oadr301_ven_client  # noqa: PLC0415

        return get_oadr301_ven_client(
            vtn_base_url=vtn_base_url,
            config=config,
        )
