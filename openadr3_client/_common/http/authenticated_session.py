# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Implementation of a HTTP session which has an associated access token that is send to every request."""

from pathlib import Path
from urllib.parse import urlparse

from requests import PreparedRequest, Session
from requests.auth import AuthBase

from openadr3_client._auth.token_manager import OAuthTokenManager
from openadr3_client._common.tls import TlsVerification
from openadr3_client.logging import logger


class _BearerAuth(AuthBase):
    """AuthBase implementation that includes a bearer token in all requests."""

    def __init__(self, token_manager: OAuthTokenManager) -> None:
        self._token_manager = token_manager

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """
        Perform the request.

        Adds the bearer token to the 'Authorization' request header before the call is made.
        If the 'Authorization' was already present, it is replaced.
        """
        # The token manager handles caching internally, so we can safely invoke this
        # for each request.
        r.headers["Authorization"] = "Bearer " + self._token_manager.get_access_token()
        return r


def _configure_tls_verification(session: Session, *, verify_tls_certificate: TlsVerification) -> None:
    """
    Apply the TLS certificate verification setting to a session.

    Logs a single warning when verification is disabled, since running without TLS verification is
    unsafe outside of development or test environments. Centralizing this here avoids duplicating the
    warning across every session/interface that accepts a verification setting.

    Args:
        session: The session to configure.
        verify_tls_certificate: See `TlsVerification`.

    """
    if not verify_tls_certificate:
        logger.warning("TLS certificate validation disabled! In most scenarios, this is a bad idea...")
    # requests annotates Session.verify as bool | str, so the Path is narrowed to str for the type contrac
    session.verify = str(verify_tls_certificate) if isinstance(verify_tls_certificate, Path) else verify_tls_certificate


class HTTPSOnlySession(Session):
    """
    Session that rejects all non HTTPS requests.

    Used directly as the anonymous (unauthenticated) session for OpenADR 3.1.0: it makes unauthenticated
    requests while preserving HTTPS enforcement and the TLS verification controls.
    """

    def __init__(self, *, verify_tls_certificate: TlsVerification = True, allow_insecure_http: bool = False) -> None:
        """
        Initializes the HTTPS-only session.

        Args:
            verify_tls_certificate: See `TlsVerification`. Defaults to True.
            allow_insecure_http: Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.

        """
        super().__init__()
        self._allow_insecure_http = allow_insecure_http
        _configure_tls_verification(self, verify_tls_certificate=verify_tls_certificate)

    def request(self, method, url, *args, **kwargs):  # noqa: ANN001, ANN202
        parsed = urlparse(url)

        if self._allow_insecure_http:
            logger.warning("HTTPS is enforced in the OpenADR 3.1.0 standard. Only use this in development or test environments, never in production.")
        if parsed.scheme != "https" and not self._allow_insecure_http:
            msg = f"Starting with openADR 3.1, HTTPS is enforced. HTTP requests are not allowed: {url}"
            raise ValueError(msg)
        return super().request(method, url, *args, **kwargs)


class BearerAuthenticatedSession(Session):
    """Session that includes a bearer token in all requests made through it."""

    def __init__(self, token_manager: OAuthTokenManager) -> None:
        super().__init__()
        self.auth = _BearerAuth(token_manager)


class UnauthenticatedSession(Session):
    """
    Session that makes anonymous (unauthenticated) requests.

    Used to connect to VTNs that do not require OAuth authentication, such as public price servers or
    development/test VTNs. This is the OpenADR 3.0.1 anonymous session; OpenADR 3.0.1 does not enforce
    HTTPS, mirroring its authenticated `BearerAuthenticatedSession`. For OpenADR 3.1.0, HTTPSOnlySession
    is used instead so that HTTPS enforcement and the TLS verification controls are preserved.
    """


class _BearerAuthenticatedHttpsOnlySession(HTTPSOnlySession):
    """Session that includes a bearer token and requires HTTPS in all requests made through it."""

    def __init__(self, token_manager: OAuthTokenManager, *, verify_tls_certificate: TlsVerification = True, allow_insecure_http: bool = False) -> None:
        """
        Initializes the Bearer Authenticated Session.

        Args:
            token_manager: The Oauth token credentials to authenticate with
            verify_tls_certificate: See `TlsVerification`. Defaults to True.
            allow_insecure_http: Whether to allow plain HTTP requests. Defaults to False. Since this is not spec-compliant, only use in development or test environments.

        """
        super().__init__(verify_tls_certificate=verify_tls_certificate, allow_insecure_http=allow_insecure_http)
        self.auth = _BearerAuth(token_manager)
