"""Contains tests for the token_manager of the auth module."""

import pytest
from oauthlib.oauth2.rfc6749.errors import InvalidClientError, InvalidScopeError, UnauthorizedClientError
from requests.exceptions import ConnectionError as requests_ConnectionError

from openadr3_client._auth.token_manager import OAuthTokenManager

from .conftest import IntegrationTestOAuthClient


def test_url_not_listening() -> None:
    """Test to verify that an error is raised if the token URL is not listening for requests."""
    manager = OAuthTokenManager(
        client_id="test", client_secret="test", token_url="https://localhost:5555/token", scopes=None
    )

    with pytest.raises(requests_ConnectionError):
        _ = manager.get_access_token()


def test_client_id_not_found(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    """Test to verify that an error is raised if a non-existent client id is given."""
    manager = OAuthTokenManager(
        client_id="wrong_client_id",
        client_secret=integration_test_oauth_client.client_secret,
        token_url=integration_test_oauth_client.token_url,
        scopes=None,
    )

    with pytest.raises(InvalidClientError):
        _ = manager.get_access_token()


def test_client_secret_wrong(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    """Test to verify that an error is raised if the wrong client secret for a client is given."""
    manager = OAuthTokenManager(
        client_id=integration_test_oauth_client.client_id,
        client_secret="wrong-test-secret",
        token_url=integration_test_oauth_client.token_url,
        scopes=None,
    )

    with pytest.raises(UnauthorizedClientError):
        _ = manager.get_access_token()


def test_non_configured_scope_for_client(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    """
    Test to verify that scopes are passed along to the OAUTH token request.

    In case of Keycloak, used in these tests, if a non configured scope is given, an error is returned.
    Note that the behaviour for what happens when scopes are given to client credential requests
    is authorization server-specific, some servers may opt to ignore the scopes completely,
    as the client already has the "keys to the kingdom" to request all scopes configured for the client
    anyway. Therefore, this only really validates that the scopes are passed along with the request,
    which is all we care about.
    """
    manager = OAuthTokenManager(
        client_id=integration_test_oauth_client.client_id,
        client_secret=integration_test_oauth_client.client_secret,
        token_url=integration_test_oauth_client.token_url,
        scopes=["test-scope"],
    )

    with pytest.raises(InvalidScopeError):
        _ = manager.get_access_token()


def test_new_token_retrieval(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    """
    Test to verify that a token is retrieved from the authorization server.

    If no token was ever retrieved with the authentication manager, no token should be cached.
    """
    manager = OAuthTokenManager(
        client_id=integration_test_oauth_client.client_id,
        client_secret=integration_test_oauth_client.client_secret,
        token_url=integration_test_oauth_client.token_url,
        scopes=None,
    )

    assert manager._cached_token is None, "No token should be cached prior to retrieval."

    token = manager.get_access_token()
    assert token is not None, "Token must not be None"
    assert token != "", "Token must not be empty"
    assert manager._cached_token is not None, "Token should be cached by manager after retrieval."


def test_cached_token_retrieval(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    """Test to verify that a token is cached after initial retrieval."""
    manager = OAuthTokenManager(
        client_id=integration_test_oauth_client.client_id,
        client_secret=integration_test_oauth_client.client_secret,
        token_url=integration_test_oauth_client.token_url,
        scopes=None,
    )

    assert manager._cached_token is None, "No token should be cached prior to retrieval."

    token = manager.get_access_token()

    assert token is not None, "Token must not be None"
    assert token != "", "Token must not be empty"
    assert manager._cached_token is not None, "Token should be cached by manager after retrieval."

    _, cached_token = manager._cached_token

    assert token == cached_token, "cached token should equal the retrieved token."

    second_retrieved_token = manager.get_access_token()

    assert second_retrieved_token == cached_token, "retrieved token should equal the cached token."
