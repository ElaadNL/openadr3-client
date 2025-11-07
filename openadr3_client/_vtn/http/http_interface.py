from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client._vtn.http.common._authenticated_session import _BearerAuthenticatedSession


class HttpInterface:
    """Represents a base class for a HTTP interface."""

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
        verify_tls_certificate: bool | str = True,
    ) -> None:
        """
        Initializes the client with a specified base URL.

        Args:
            base_url (str): The base URL for the HTTP interface.
            config (OAuthTokenManagerConfig): The configuration for the OAuth token manager.
            verify_vtn_tls_certificate (bool | str): Whether the VEN verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.
        """
        if base_url is None:
            msg = "base_url is required"
            raise ValueError(msg)
        self.base_url = base_url
        self.session = _BearerAuthenticatedSession(token_manager=OAuthTokenManager(config), verify_tls_certificate=verify_tls_certificate)
