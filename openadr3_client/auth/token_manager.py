from threading import Lock
from typing import Optional
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from cachetools import TTLCache
from openadr3_client.logging import logger

class OAuthTokenManager:
    def __init__(self, client_id: str, client_secret: str, token_url: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.client = BackendApplicationClient(client_id=self.client_id)
        self.oauth = OAuth2Session(client=self.client)

        self._lock = Lock()
        self._cache: Optional[TTLCache] = None

    def get_access_token(self) -> str:
        """Retrieves an access token from the token manager.

        If a cached token is present in the token manager, this token is returned.
        If no cached token is present, a new token is fetched, cached and returned.

        Returns:
            str: The access token.
        """
        with self._lock:
            if self._cache:
                token = self._cache.get("token")

                if token:
                    logger.debug("OAuthTokenManager - Returning cached access token")
                    return token
                
            logger.debug("OAuthTokenManager - Fetching new access token")
            return self._get_new_access_token()
    
    def _get_new_access_token(self) -> str:
        token_response = self.oauth.fetch_token(token_url=self.token_url, client_secret=self.client_secret)

        # Calculate dynamic TTL (half of token lifetime)
        expires_in_seconds = token_response.get("expires_in", 3600)
        self._cache = TTLCache(maxsize=1, ttl=expires_in_seconds // 2)

        access_token = token_response.get("access_token")

        if not access_token:
            logger.error("OAuthTokenManager - access_token not present in token response")
            raise ValueError("Access token was not present in token response")

        self._cache['token'] = access_token
        return access_token