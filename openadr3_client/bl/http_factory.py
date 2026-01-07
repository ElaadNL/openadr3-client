from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.bl._client import BaseBusinessLogicClient
from openadr3_client.logging import logger
from openadr3_client.version import OADRVersion


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
        version: OADRVersion,
    ) -> BaseBusinessLogicClient:
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
            version (OADRVersion): The OpenADR version to use. Defaults to OADR_310.

        Returns:
            BaseBusinessLogicClient: The business logic client instance.

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
                logger.info("Token URL not provided to BL client factory, calling VTN discovery endpoint to fetch token URL...")
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

        if version == OADRVersion.OADR_310:
            from openadr3_client.oadr310._bl.client import get_oadr310_bl_client  # noqa: PLC0415

            return get_oadr310_bl_client(
                vtn_base_url=vtn_base_url,
                config=config,
                verify_vtn_tls_certificate=verify_vtn_tls_certificate,
            )

        from openadr3_client.oadr301._bl.client import get_oadr301_bl_client  # noqa: PLC0415

        return get_oadr301_bl_client(
            vtn_base_url=vtn_base_url,
            config=config,
        )
