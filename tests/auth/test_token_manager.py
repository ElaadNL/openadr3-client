"""Contains tests for the token_manager of the auth module."""

import pytest
from .conftest import IntegrationTestOAuthClient
from openadr3_client.auth.token_manager import OAuthTokenManager
from requests.exceptions import ConnectionError
from oauthlib.oauth2.rfc6749.errors import InvalidClientError, UnauthorizedClientError, InvalidScopeError

def test_url_not_listening() -> None:
    manager = OAuthTokenManager(client_id="test",
                                client_secret="test",
                                token_url="https://localhost:5555/token",
                                scopes=None)
    
    with pytest.raises(ConnectionError):
        _ = manager.get_access_token()
1
def test_client_id_not_found(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    manager = OAuthTokenManager(client_id="wrong_client_id",
                                client_secret=integration_test_oauth_client.client_secret,
                                token_url=integration_test_oauth_client.token_url,
                                scopes=None)
    
    with pytest.raises(InvalidClientError):
        _ = manager.get_access_token()
    

def test_client_secret_wrong(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    manager = OAuthTokenManager(client_id=integration_test_oauth_client.client_id,
                                client_secret="wrong-test-secret",
                                token_url=integration_test_oauth_client.token_url,
                                scopes=None)
    
    with pytest.raises(UnauthorizedClientError):
        _ = manager.get_access_token()

def test_non_existent_client(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    manager = OAuthTokenManager(client_id="non-existent-client",
                                client_secret="fancy-secret-value",
                                token_url=integration_test_oauth_client.token_url,
                                scopes=None)
    
    with pytest.raises(InvalidClientError):
        _ = manager.get_access_token()

def test_non_configured_scope_for_client(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    """Test to verify that scopes are passed along to the OAUTH token request.
    
    In case of Keycloak, used in these tests, if a non configured scope is given, an error is returned.
    Note that the behaviour for what happens when scopes are given to client credential requests
    is authorization server-specific, some servers may opt to ignore the scopes completely,
    as the client already has the "keys to the kingdom" to request all scopes configured for the client
    anyway. Therefore, this only really validates that the scopes are passed along with the request,
    which is all we care about.
    """
    manager = OAuthTokenManager(client_id=integration_test_oauth_client.client_id,
                                client_secret=integration_test_oauth_client.client_secret,
                                token_url=integration_test_oauth_client.token_url,
                                scopes=["test-scope"])
    
    with pytest.raises(InvalidScopeError):
        _ = manager.get_access_token()

def test_new_token_retrieval(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    manager = OAuthTokenManager(client_id=integration_test_oauth_client.client_id,
                                client_secret=integration_test_oauth_client.client_secret,
                                token_url=integration_test_oauth_client.token_url,
                                scopes=None)
    
    token = manager.get_access_token()
    assert token is not None and token != "", "Token must not be None or empty"

def test_cached_token_retrieval(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:

    manager = OAuthTokenManager(client_id=integration_test_oauth_client.client_id,
                                client_secret=integration_test_oauth_client.client_secret,
                                token_url=integration_test_oauth_client.token_url,
                                scopes=None)
    
    cached_token_before_call = manager._cached_token
    
    token = manager.get_access_token()

    assert token is not None and token != "", "Token must not be None or empty"

    assert cached_token_before_call is None
    assert manager._cached_token is not None

    _, cached_token = manager._cached_token

    assert token == cached_token

    second_retrieved_token = manager.get_access_token()

    assert second_retrieved_token == cached_token