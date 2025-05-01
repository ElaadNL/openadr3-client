"""Implementation of a HTTP session which has an associated access token that is send to every request."""

from requests import PreparedRequest, Session
from requests.auth import AuthBase

from openadr3_client._auth.token_manager import OAuthTokenManager
from openadr3_client.config import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_SCOPES, OAUTH_TOKEN_ENDPOINT


class _BearerAuth(AuthBase):
    """AuthBase implementation that includes a bearer token in all requests."""

    def __init__(self) -> None:
        self._token_manager = OAuthTokenManager(
            client_id=OAUTH_CLIENT_ID,
            client_secret=OAUTH_CLIENT_SECRET,
            token_url=OAUTH_TOKEN_ENDPOINT,
            scopes=OAUTH_SCOPES,
        )

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


class _BearerAuthenticatedSession(Session):
    """Session that includes a bearer token in all requests made through it."""

    def __init__(self) -> None:
        super().__init__()
        self.auth = _BearerAuth()


bearer_authenticated_session = _BearerAuthenticatedSession()
