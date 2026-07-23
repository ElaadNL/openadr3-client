# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from typing import final

from openadr3_client._auth.config_builder import build_token_manager_config
from openadr3_client.bl._client import BaseBusinessLogicClient
from openadr3_client.version import OADRVersion


@final
class BusinessLogicHttpClientFactory:
    """Factory which can be used to create a business logic http client."""

    @staticmethod
    def create_http_bl_client(
        vtn_base_url: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        token_url: str | None = None,
        scopes: list[str] | None = None,
        audience: str | None = None,
        *,
        verify_vtn_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
        version: OADRVersion,
    ) -> BaseBusinessLogicClient:
        """
        Creates a business logic client which uses the HTTP interface of a VTN.

        To connect to a VTN that does not require authentication (for example a development/test VTN),
        omit both client_id and client_secret. The client then makes anonymous (unauthenticated) requests
        and no OAuth token is provisioned.

        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.
            client_id (str | None): The client id to use to provision an access token from the OAuth authorization server.
            Omit (or None) together with client_secret to create an anonymous, unauthenticated client.
            client_secret (str | None): The client secret to use to provision an access token from the OAuth authorization server.
            Omit (or None) together with client_id to create an anonymous, unauthenticated client.
            token_url (str | None): The endpoint to provision access tokens from. Defaults to None. If None, the token URL is discovered by calling
            the discover endpoint (introduced in OpenADR 3.1) on the OpenADR VTN. Ignored for anonymous clients.
            scopes (list[str]): The scopes to request with the token. If empty, no scopes are requested.
            audience (str): The audience to request with the token. If empty, no audience is requested.
            verify_vtn_tls_certificate (bool | str): Whether the BL verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.
            allow_insecure_http (bool): Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.
            version (OADRVersion): The OpenADR version to use. Defaults to OADR_310.

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
