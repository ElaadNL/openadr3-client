"""Implementation of a HTTP session which has an associated access token that is send to every request."""

from urllib.parse import urljoin
from requests import Session
from requests.auth import AuthBase

from openadr3_client.auth.token_manager import OAuthTokenManager
from openadr3_client.config import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_TOKEN_ENDPOINT, OAUTH_SCOPES, VTN_BASE_URL

class _BearerAuth(AuthBase):
    """AuthBase implementation that includes a bearer token in all requests."""

    def __init__(self) -> None:
        self._token_manager = OAuthTokenManager(
            client_id=OAUTH_CLIENT_ID,
            client_secret=OAUTH_CLIENT_SECRET,
            token_url=OAUTH_TOKEN_ENDPOINT,
            scopes=OAUTH_SCOPES,
        )
    def __call__(self, r):
        """Perform the request.
        
        Adds the bearer token to the 'Authorization' request header before the call is made.
        If the 'Authorization' was already present, it is replaced.
        """

        # The token manager handles caching internally, so we can safely invoke this
        # for each request.
        r.headers["Authorization"] = "Bearer " + self._token_manager.get_access_token()

class _BaseUrlPrependedSession(Session):
    """Session that prepends the configured VTN base URL in all requests made through it."""
    def __init__(self):
        super().__init__()
        self.base_url = VTN_BASE_URL

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)

class _BearerAuthenticatedSession(_BaseUrlPrependedSession):
    """Session that includes a bearer token in all requests made through it."""
    def __init__(self) -> None:
        self.auth = _BearerAuth()


bearer_authenticated_session = _BearerAuthenticatedSession()