# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client._common.http.authenticated_session import BearerAuthenticatedSession, UnauthenticatedSession


class HttpInterface:
    """
    Represents a base class for a HTTP interface.

    When ``config`` is ``None``, the interface makes anonymous (unauthenticated)
    requests instead, for connecting to VTNs that do not require OAuth.
    """

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig | None,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            config (OAuthTokenManagerConfig | None): The configuration for the OAuth token manager. If None, an
            anonymous (unauthenticated) session is used instead of a bearer-authenticated one.

        """
        if base_url is None:
            msg = "base_url is required"
            raise ValueError(msg)
        self.base_url = base_url
        self.session = UnauthenticatedSession() if config is None else BearerAuthenticatedSession(OAuthTokenManager(config))
