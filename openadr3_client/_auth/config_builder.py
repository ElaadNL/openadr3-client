# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Shared helper for building the OAuth token manager configuration from client factory arguments."""

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.logging import logger
from openadr3_client.version import OADRVersion


def build_token_manager_config(
    *,
    client_id: str | None,
    client_secret: str | None,
    token_url: str | None,
    scopes: list[str] | None,
    audience: str | None,
    vtn_base_url: str,
    verify_vtn_tls_certificate: bool | str,
    version: OADRVersion,
    factory_name: str,
) -> OAuthTokenManagerConfig | None:
    """
    Builds the OAuth token manager configuration for a client factory.

    Returns None when an anonymous (unauthenticated) client is requested, which is the case when neither
    client_id nor client_secret is provided. An anonymous client makes unauthenticated requests, for
    connecting to VTNs that do not require OAuth (for example public price servers or development/test VTNs).
    Anonymous clients are intended for reading public data; write and registration operations are still
    sent, but a VTN that gates them behind authentication will reject them.

    Args:
        client_id: The OAuth client id, or None for an anonymous client.
        client_secret: The OAuth client secret, or None for an anonymous client.
        token_url: The endpoint to provision access tokens from. If None and the client is authenticated, the
        token URL is discovered from the VTN discovery endpoint (OpenADR 3.1.0 only).
        scopes: The scopes to request with the token.
        audience: The audience to request with the token.
        vtn_base_url: The base URL for the HTTP interface of the VTN, used for token URL discovery.
        verify_vtn_tls_certificate: Whether to verify the TLS certificate of the VTN during discovery.
        version: The OpenADR version to use.
        factory_name: A human readable name of the calling factory, used in log messages.

    Returns:
        OAuthTokenManagerConfig | None: The token manager configuration, or None for an anonymous client.

    """
    # An anonymous (unauthenticated) client is requested when no client credentials are provided.
    if client_id is None and client_secret is None:
        return None

    # Providing only one of the two credentials is a misconfiguration.
    if client_id is None or client_secret is None:
        msg = "Both client_id and client_secret must be provided for an authenticated client, or both omitted for an anonymous client."
        raise ValueError(msg)

    # Starting with OpenADR 3.1.0, the token URL can be discovered from the VTN through the discovery endpoint.
    # This is only done if the token_url has not been manually provided.
    if token_url is None:
        if version == OADRVersion.OADR_301:
            msg = "Token URL must be provided for OpenADR 3.0.1 clients."
            raise ValueError(msg)
        if version == OADRVersion.OADR_310:
            from openadr3_client.oadr310._vtn.http.auth import AuthReadOnlyInterface  # noqa: PLC0415

            # If token URL is None, discover the token URL from the VTN through the discovery endpoint.
            logger.info(f"Token URL not provided to {factory_name}, calling VTN discovery endpoint to fetch token URL...")
            auth_interface = AuthReadOnlyInterface(base_url=vtn_base_url, verify_tls_certificate=verify_vtn_tls_certificate)
            auth_server_info = auth_interface.get_auth_server()
            token_url = auth_server_info.token_url

    return OAuthTokenManagerConfig(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url,
        scopes=scopes,
        audience=audience,
    )
