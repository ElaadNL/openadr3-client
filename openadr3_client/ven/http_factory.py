# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from typing import final

from openadr3_client._auth.config_builder import build_token_manager_config
from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client._common.tls import TlsVerification, normalize_tls_verification
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
        token_url: str | None = None,
        scopes: list[str] | None = None,
        *,
        verify_vtn_tls_certificate: TlsVerification | str = True,
        allow_insecure_http: bool = False,
        version: OADRVersion,
    ) -> BaseVirtualEndNodeClient:
        """
        Creates an authenticated VEN client which uses the HTTP interface of a VTN.

        To connect to a VTN that does not require authentication (for example a public price server or a
        development/test VTN), use `create_anonymous_http_ven_client` instead.

        Args:
            vtn_base_url: The base URL for the HTTP interface of the VTN.
            client_id: The client id to use to provision an access token from the OAuth authorization server.
            client_secret: The client secret to use to provision an access token from the OAuth authorization server.
            token_url: The endpoint to provision access tokens from. Defaults to None. If None, the token URL is discovered by calling
            the discover endpoint (introduced in OpenADR 3.1) on the OpenADR VTN.
            scopes: The scopes to request with the token. If empty, no scopes are requested.
            verify_vtn_tls_certificate: See `TlsVerification`. Defaults to True. Passing a str path to a CA
            certificate bundle is deprecated, pass a `pathlib.Path` instead.
            allow_insecure_http: Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.
            version: The OpenADR version to use for the VEN client.

        """
        verify_tls = normalize_tls_verification(verify_vtn_tls_certificate)
        config = build_token_manager_config(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=None,
            vtn_base_url=vtn_base_url,
            verify_vtn_tls_certificate=verify_tls,
            version=version,
            factory_name="VEN client factory",
        )
        return VirtualEndNodeHttpClientFactory._create_ven_client(
            vtn_base_url=vtn_base_url,
            config=config,
            verify_vtn_tls_certificate=verify_tls,
            allow_insecure_http=allow_insecure_http,
            version=version,
        )

    @staticmethod
    def create_anonymous_http_ven_client(
        vtn_base_url: str,
        *,
        verify_vtn_tls_certificate: TlsVerification | str = True,
        allow_insecure_http: bool = False,
        version: OADRVersion,
    ) -> BaseVirtualEndNodeClient:
        """
        Creates an anonymous (unauthenticated) VEN client which uses the HTTP interface of a VTN.

        No OAuth token is provisioned and requests are sent unauthenticated, for connecting to VTNs that do
        not require OAuth (for example a public price server or a development/test VTN). This is intended for
        reading public data (such as Programs and Events); write and registration operations are still sent,
        but a VTN that gates them behind authentication will reject them.

        Args:
            vtn_base_url: The base URL for the HTTP interface of the VTN.
            verify_vtn_tls_certificate: See `TlsVerification`. Defaults to True. Passing a str path to a CA
            certificate bundle is deprecated, pass a `pathlib.Path` instead.
            allow_insecure_http: Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.
            version: The OpenADR version to use for the VEN client.

        """
        return VirtualEndNodeHttpClientFactory._create_ven_client(
            vtn_base_url=vtn_base_url,
            config=None,
            verify_vtn_tls_certificate=normalize_tls_verification(verify_vtn_tls_certificate),
            allow_insecure_http=allow_insecure_http,
            version=version,
        )

    @staticmethod
    def _create_ven_client(
        vtn_base_url: str,
        config: OAuthTokenManagerConfig | None,
        *,
        verify_vtn_tls_certificate: TlsVerification,
        allow_insecure_http: bool,
        version: OADRVersion,
    ) -> BaseVirtualEndNodeClient:
        """Dispatches to the version-specific VEN client. `config` is None for an anonymous client."""
        if version == OADRVersion.OADR_310:
            from openadr3_client.oadr310._ven.client import get_oadr310_ven_client  # noqa: PLC0415

            return get_oadr310_ven_client(
                vtn_base_url=vtn_base_url,
                config=config,
                verify_vtn_tls_certificate=verify_vtn_tls_certificate,
                allow_insecure_http=allow_insecure_http,
            )

        from openadr3_client.oadr301._ven.client import get_oadr301_ven_client  # noqa: PLC0415

        return get_oadr301_ven_client(
            vtn_base_url=vtn_base_url,
            config=config,
        )
