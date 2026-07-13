# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Version-neutral authenticated HTTP base for the resource group extension."""

from requests import Session

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client._common.http.authenticated_session import _BearerAuthenticatedHttpsOnlySession


class _BaseHttpInterface:
    """Base class holding the base URL and requests session."""

    def __init__(self, base_url: str, session: Session) -> None:
        self.base_url = base_url
        self.session = session


class AuthenticatedHttpInterface(_BaseHttpInterface):
    """HTTP interface that attaches a bearer token to every request."""

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
        *,
        verify_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
    ) -> None:
        session = _BearerAuthenticatedHttpsOnlySession(
            token_manager=OAuthTokenManager(config),
            verify_tls_certificate=verify_tls_certificate,
            allow_insecure_http=allow_insecure_http,
        )
        super().__init__(base_url=base_url, session=session)
