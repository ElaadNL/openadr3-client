# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Factory for constructing resource group clients (BL read-write, VEN read-only)."""

from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
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
        verify_vtn_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
    ) -> ReadWriteResourceGroupsInterface:
        """Create a BL (read-write) resource group client."""
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
            verify_tls_certificate=verify_vtn_tls_certificate,
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
        verify_vtn_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
    ) -> ReadOnlyResourceGroupsInterface:
        """Create a VEN (read-only) resource group client."""
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
            verify_tls_certificate=verify_vtn_tls_certificate,
            allow_insecure_http=allow_insecure_http,
        )
