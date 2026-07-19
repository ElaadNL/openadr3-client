# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from typing import final

from openadr3_client._auth.config_builder import build_token_manager_config
from openadr3_client.ven._client import BaseVirtualEndNodeClient
from openadr3_client.version import OADRVersion


@final
class VirtualEndNodeHttpClientFactory:
    """Factory which can be used to create a virtual end node (VEN) http client."""

    @staticmethod
    def create_http_ven_client(
        vtn_base_url: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        token_url: str | None = None,
        scopes: list[str] | None = None,
        *,
        verify_vtn_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
        version: OADRVersion,
    ) -> BaseVirtualEndNodeClient:
        """
        Creates a VEN client which uses the HTTP interface of a VTN.

        To connect to a VTN that does not require authentication (for example a public price server or a
        development/test VTN), omit both client_id and client_secret. The client then makes anonymous
        (unauthenticated) requests and no OAuth token is provisioned.

        Args:
            vtn_base_url: The base URL for the HTTP interface of the VTN.
            client_id: The client id to use to provision an access token from the OAuth authorization server.
            Omit (or None) together with client_secret to create an anonymous, unauthenticated client.
            client_secret: The client secret to use to provision an access token from the OAuth authorization server.
            Omit (or None) together with client_id to create an anonymous, unauthenticated client.
            token_url: The endpoint to provision access tokens from. Defaults to None. If None, the token URL is discovered by calling
            the discover endpoint (introduced in OpenADR 3.1) on the OpenADR VTN. Ignored for anonymous clients.
            scopes: The scopes to request with the token. If empty, no scopes are requested.
            verify_vtn_tls_certificate: Whether the VEN verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.
            allow_insecure_http: Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.
            version: The OpenADR version to use for the VEN client. Defaults to OADR 3.1.0.

        """
        config = build_token_manager_config(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=None,
            vtn_base_url=vtn_base_url,
            verify_vtn_tls_certificate=verify_vtn_tls_certificate,
            version=version,
            factory_name="VEN client factory",
        )

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
