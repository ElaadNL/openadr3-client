# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from typing import final

from openadr3_client._auth.config_builder import build_token_manager_config
from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.bl._client import BaseBusinessLogicClient
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
        allow_insecure_http: bool = False,
        version: OADRVersion,
    ) -> BaseBusinessLogicClient:
        """
        Creates an authenticated business logic client which uses the HTTP interface of a VTN.

        To connect to a VTN that does not require authentication (for example a development/test VTN), use
        `create_anonymous_http_bl_client` instead.

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
            allow_insecure_http (bool): Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.
            version (OADRVersion): The OpenADR version to use.

        Returns:
            BaseBusinessLogicClient: The business logic client instance.

        """  # noqa: E501
        config = build_token_manager_config(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=audience,
            vtn_base_url=vtn_base_url,
            verify_vtn_tls_certificate=verify_vtn_tls_certificate,
            version=version,
            factory_name="BL client factory",
        )
        return BusinessLogicHttpClientFactory._create_bl_client(
            vtn_base_url=vtn_base_url,
            config=config,
            verify_vtn_tls_certificate=verify_vtn_tls_certificate,
            allow_insecure_http=allow_insecure_http,
            version=version,
        )

    @staticmethod
    def create_anonymous_http_bl_client(
        vtn_base_url: str,
        *,
        verify_vtn_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
        version: OADRVersion,
    ) -> BaseBusinessLogicClient:
        """
        Creates an anonymous (unauthenticated) business logic client which uses the HTTP interface of a VTN.

        No OAuth token is provisioned and requests are sent unauthenticated, for connecting to VTNs that do
        not require OAuth (for example a development/test VTN). This is intended for reading public data (such
        as Programs and Events); write and registration operations are still sent, but a VTN that gates them
        behind authentication will reject them.

        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.
            verify_vtn_tls_certificate (bool | str): Whether the BL verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.
            allow_insecure_http (bool): Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.
            version (OADRVersion): The OpenADR version to use.

        Returns:
            BaseBusinessLogicClient: The business logic client instance.

        """  # noqa: E501
        return BusinessLogicHttpClientFactory._create_bl_client(
            vtn_base_url=vtn_base_url,
            config=None,
            verify_vtn_tls_certificate=verify_vtn_tls_certificate,
            allow_insecure_http=allow_insecure_http,
            version=version,
        )

    @staticmethod
    def _create_bl_client(
        vtn_base_url: str,
        config: OAuthTokenManagerConfig | None,
        *,
        verify_vtn_tls_certificate: bool | str,
        allow_insecure_http: bool,
        version: OADRVersion,
    ) -> BaseBusinessLogicClient:
        """Dispatches to the version-specific BL client. `config` is None for an anonymous client."""
        if version == OADRVersion.OADR_310:
            from openadr3_client.oadr310._bl.client import get_oadr310_bl_client  # noqa: PLC0415

            return get_oadr310_bl_client(
                vtn_base_url=vtn_base_url,
                config=config,
                verify_vtn_tls_certificate=verify_vtn_tls_certificate,
                allow_insecure_http=allow_insecure_http,
            )

        from openadr3_client.oadr301._bl.client import get_oadr301_bl_client  # noqa: PLC0415

        return get_oadr301_bl_client(
            vtn_base_url=vtn_base_url,
            config=config,
        )
