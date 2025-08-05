from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client._vtn.http.common._authenticated_session import _BearerAuthenticatedSession


class HttpInterface:
    """Represents a base class for a HTTP interface."""

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            config (OAuthTokenManagerConfig): The configuration for the OAuth token manager.

        """
        if base_url is None:
            msg = "base_url is required"
            raise ValueError(msg)
        self.base_url = base_url
        self.session = _BearerAuthenticatedSession(OAuthTokenManager(config))
