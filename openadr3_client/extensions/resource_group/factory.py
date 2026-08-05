# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Factory for constructing resource group clients (BL read-write, VEN read-only)."""

from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client._common.tls import TlsVerification, normalize_tls_verification
from openadr3_client.extensions.resource_group._client.http import (
    ResourceGroupsHttpInterface,
    ResourceGroupsReadOnlyHttpInterface,
)
from openadr3_client.extensions.resource_group._client.interfaces import (
    ReadOnlyResourceGroupsInterface,
    ReadWriteResourceGroupsInterface,
)


@final
class ResourceGroupClientFactory:
    """
    Factory for resource group HTTP clients.

    Hardcodes no OAuth scope. Recommended scopes: BL = ["read_all", "write_programs"];
    VEN = ["read_ven_objects"] (own-only obfuscated read).
    """

    @staticmethod
    def create_bl_client(
        vtn_base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        scopes: list[str] | None = None,
        audience: str | None = None,
        *,
        verify_vtn_tls_certificate: TlsVerification | str = True,
        allow_insecure_http: bool = False,
    ) -> ReadWriteResourceGroupsInterface:
        """
        Create a BL (read-write) resource group client.

        Args:
            vtn_base_url: The base URL for the HTTP interface of the VTN.
            client_id: The client id to use to provision an access token from the OAuth authorization server.
            client_secret: The client secret to use to provision an access token from the OAuth authorization server.
            token_url: The endpoint to provision access tokens from.
            scopes: The scopes to request with the token. If empty, no scopes are requested.
            audience: The audience to request with the token. If empty, no audience is requested.
            verify_vtn_tls_certificate: See `TlsVerification`. Defaults to True. Passing a str path to a CA
            certificate bundle is deprecated, pass a `pathlib.Path` instead.
            allow_insecure_http: Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.

        """
        config = OAuthTokenManagerConfig(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=audience,
        )
        return ResourceGroupsHttpInterface(
            base_url=vtn_base_url,
            config=config,
            verify_tls_certificate=normalize_tls_verification(verify_vtn_tls_certificate),
            allow_insecure_http=allow_insecure_http,
        )

    @staticmethod
    def create_ven_client(
        vtn_base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        scopes: list[str] | None = None,
        audience: str | None = None,
        *,
        verify_vtn_tls_certificate: TlsVerification | str = True,
        allow_insecure_http: bool = False,
    ) -> ReadOnlyResourceGroupsInterface:
        """
        Create a VEN (read-only) resource group client.

        Args:
            vtn_base_url: The base URL for the HTTP interface of the VTN.
            client_id: The client id to use to provision an access token from the OAuth authorization server.
            client_secret: The client secret to use to provision an access token from the OAuth authorization server.
            token_url: The endpoint to provision access tokens from.
            scopes: The scopes to request with the token. If empty, no scopes are requested.
            audience: The audience to request with the token. If empty, no audience is requested.
            verify_vtn_tls_certificate: See `TlsVerification`. Defaults to True. Passing a str path to a CA
            certificate bundle is deprecated, pass a `pathlib.Path` instead.
            allow_insecure_http: Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.

        """
        config = OAuthTokenManagerConfig(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=audience,
        )
        return ResourceGroupsReadOnlyHttpInterface(
            base_url=vtn_base_url,
            config=config,
            verify_tls_certificate=normalize_tls_verification(verify_vtn_tls_certificate),
            allow_insecure_http=allow_insecure_http,
        )
