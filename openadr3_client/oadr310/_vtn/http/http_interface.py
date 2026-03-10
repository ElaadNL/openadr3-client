# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from requests import Session

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client._common.http.authenticated_session import _BearerAuthenticatedHttpsOnlySession
from openadr3_client.logging import logger


class _BaseHttpInterface:
    """Represents a base class for all HTTP interface of the OpenADR3 client."""

    def __init__(
        self,
        base_url: str,
        session: Session,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            session (Session): The requests session to use when communicating through HTTP(S).

        """
        if base_url is None:
            msg = "base_url is required"
            raise ValueError(msg)
        self.base_url = base_url
        self.session = session


class AnonymousHttpInterface(_BaseHttpInterface):
    """Represents an HTTP interface that makes anonymous (unauthenticated) requests."""

    def __init__(
        self,
        base_url: str,
        *,
        verify_tls_certificate: bool | str = True,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            verify_tls_certificate (bool | str): Whether the VEN verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.

        """
        session = Session()

        if not verify_tls_certificate:
            logger.warning("TLS certificate validation disabled! In most scenarios, this is a bad idea...")
        session.verify = verify_tls_certificate
        super().__init__(base_url=base_url, session=session)


class AuthenticatedHttpInterface(_BaseHttpInterface):
    """Represents an HTTP interface that makes authenticated requests."""

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
        *,
        verify_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            config (OAuthTokenManagerConfig): The configuration for the OAuth token manager.
            verify_tls_certificate (bool | str): Whether the VEN verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.
            allow_insecure_http (bool): Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.

        """  # noqa: E501
        authenticated_session = _BearerAuthenticatedHttpsOnlySession(
            token_manager=OAuthTokenManager(config),
            verify_tls_certificate=verify_tls_certificate,
            allow_insecure_http=allow_insecure_http,
        )
        super().__init__(base_url=base_url, session=authenticated_session)
