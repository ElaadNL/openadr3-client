"""Module containing fixtures relevant for testing the authentication module."""

from typing import Iterable
import pytest

from testcontainers.keycloak import KeycloakContainer

import logging

# Set up logging for the testcontainers package
logging.basicConfig(level=logging.DEBUG)  # Or INFO if you want less noise


class IntegrationTestOAuthClient:
    def __init__(self, client_id: str, client_secret: str, token_url: str) -> None:
        """Initializes the IntegrationTestOAuthClient.

        Args:
            client_id (str): the client id.
            client_secret (str): The client secret.
            token_url (str): The token URL to fetch tokens from.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url


@pytest.fixture(scope='session')
def integration_test_oauth_client() -> Iterable[IntegrationTestOAuthClient]:
    """A testcontainers keycloak fixture which is initialized once per test run.

    Yields an IntegrationTestOAuthClient which contains an oauth client that was created
    for the scope of this test session.

    Yields:
        Generator[IntegrationTestOAuthClient]: The intregration test oauth client.
    """
    with KeycloakContainer() as keycloak:
        client = keycloak.get_client()
        
        # Create the integration test keycloak realm.
        realm_name = "integration-test-realm"
        client.create_realm(payload={
            "realm": realm_name,
            "enabled": True
        })

        client_id = "test-client-id"
        client_secret = "my-client-secret"

        client.change_current_realm(realm_name)
        client.create_client(       
            payload={
                "clientId": client_id,
                "enabled": True,
                "clientAuthenticatorType": "client-secret",
                "secret": client_secret,
                "protocol": "openid-connect",
                "publicClient": False,
                "directAccessGrantsEnabled": True,
                "serviceAccountsEnabled": True
            }
        )

        token_url = keycloak.get_url() + f"/realms/{realm_name}/protocol/openid-connect/token"
        yield IntegrationTestOAuthClient(client_id, client_secret, token_url)