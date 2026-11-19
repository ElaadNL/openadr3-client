# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client._common.http.authenticated_session import (
    HTTPSOnlySession,
    _BearerAuthenticatedHttpsOnlySession,
    _configure_tls_verification,
    _TimeoutSession,
)
from openadr3_client._common.http.timeout import DEFAULT_HTTP_TIMEOUT, HttpTimeout
from openadr3_client._common.tls import TlsVerification


class _BaseHttpInterface:
    """Represents a base class for all HTTP interface of the OpenADR3 client."""

    def __init__(
        self,
        base_url: str,
        session: _TimeoutSession,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            session (_TimeoutSession): The requests session to use when communicating through HTTP(S).

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
        verify_tls_certificate: TlsVerification = True,
        timeout: HttpTimeout = DEFAULT_HTTP_TIMEOUT,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            verify_tls_certificate: See `TlsVerification`. Defaults to True.
            timeout: See `HttpTimeout`. Defaults to `DEFAULT_HTTP_TIMEOUT`.

        """
        session = _TimeoutSession(timeout=timeout)
        _configure_tls_verification(session, verify_tls_certificate=verify_tls_certificate)
        super().__init__(base_url=base_url, session=session)


class AuthenticatedHttpInterface(_BaseHttpInterface):
    """
    Represents an HTTP interface that makes authenticated requests.

    When ``config`` is ``None``, the interface makes anonymous (unauthenticated)
    requests instead, for connecting to VTNs that do not require OAuth (for
    example public price servers or development/test VTNs).
    """

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig | None,
        *,
        verify_tls_certificate: TlsVerification = True,
        allow_insecure_http: bool = False,
        timeout: HttpTimeout = DEFAULT_HTTP_TIMEOUT,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            config (OAuthTokenManagerConfig | None): The configuration for the OAuth token manager. If None, an
            anonymous (unauthenticated) session is used instead of a bearer-authenticated one.
            verify_tls_certificate: See `TlsVerification`. Defaults to True.
            allow_insecure_http (bool): Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.
            timeout: See `HttpTimeout`. Defaults to `DEFAULT_HTTP_TIMEOUT`.

        """  # noqa: E501
        session = (
            HTTPSOnlySession(
                verify_tls_certificate=verify_tls_certificate,
                allow_insecure_http=allow_insecure_http,
                timeout=timeout,
            )
            if config is None
            else _BearerAuthenticatedHttpsOnlySession(
                token_manager=OAuthTokenManager(config),
                verify_tls_certificate=verify_tls_certificate,
                allow_insecure_http=allow_insecure_http,
                timeout=timeout,
            )
        )
        super().__init__(base_url=base_url, session=session)
