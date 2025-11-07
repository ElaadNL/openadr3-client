"""Implementation of a HTTP session which has an associated access token that is send to every request."""

from urllib.parse import urlparse
from requests import PreparedRequest, Session
from requests.auth import AuthBase

from openadr3_client._auth.token_manager import OAuthTokenManager


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

class HTTPSOnlySession(Session):
    """Session that rejects all non HTTPS requests."""
    def request(self, method, url, *args, **kwargs):
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise ValueError(f"Starting with openADR 3.1, HTTPS is enforced. HTTP requests are not allowed: {url}")
        return super().request(method, url, *args, **kwargs)
    

class _BearerAuthenticatedSession(HTTPSOnlySession):
    """Session that includes a bearer token in all requests made through it."""

    def __init__(self, token_manager: OAuthTokenManager, verify_tls_certificate: bool | str = True) -> None:
        """Initializes the Bearer Authenticated Session

        Args:
            token_manager (OAuthTokenManager): The Oauth token credentials to authenticate with
            verify_vtn_tls_certificate (bool | str): Whether the VEN verifies the TLS certificate of the VTN.
            Defaults to True to validate the TLS certificate against known CAs. Can be set to False to disable verification (not recommended).
            If a string is given as value, it is assumed that a custom CA certificate bundle (.PEM) is provided for a self signed CA. In this case, the
            PEM file must contain the entire certificate chain including intermediate certificates required to validate the servers certificate.
        """
        super().__init__()
        self.auth = _BearerAuth(token_manager)
        self.verify = verify_tls_certificate
