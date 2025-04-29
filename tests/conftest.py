"""Module containing fixtures relevant for testing the authentication module."""

import base64
import logging
from collections.abc import Iterable
import tempfile

import pytest
import requests
from testcontainers.keycloak import KeycloakContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.core.network import Network
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from unittest.mock import patch

from openadr3_client.config import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_TOKEN_ENDPOINT

# Set up logging for the testcontainers package
logging.basicConfig(level=logging.DEBUG)

class IntegrationTestVTNClient:
    """
    Class containing an OpenADR3 VTN client configured for use in integration tests.

    This client is configured as a generic docker testcontainer and is guaranteed
    to exist for the duration of the integration tests.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initializes the IntegrationTestOAuthClient.

        Args:
            client_id (str): the client id.
            client_secret (str): The client secret.
            token_url (str): The token URL to fetch tokens from.

        """
        self.vtn_base_url = base_url

class IntegrationTestOAuthClient:
    """
    Class containing an OAUTH client configured for use in integration tests.

    This client is configured inside the keycloak testcontainer and is guaranteed
    to exist for the duration of the integration tests.
    """

    def __init__(self, client_id: str, client_secret: str, token_url: str, jwks_url: str) -> None:
        """
        Initializes the IntegrationTestOAuthClient.

        Args:
            client_id (str): the client id.
            client_secret (str): The client secret.
            token_url (str): The token URL to fetch tokens from.
            jwks_url (str): The jwks uri to fetch keys from.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.jwks_url = jwks_url

def base64url_decode(value):
    """Decodes a base64 URL-safe string with padding."""
    value += '=' * (-len(value) % 4)  # Add padding if necessary
    return base64.urlsafe_b64decode(value)

def jwk_to_pem(jwk):
    """Convert JWK to PEM format."""
    n = int.from_bytes(base64url_decode(jwk['n']), 'big')
    e = int.from_bytes(base64url_decode(jwk['e']), 'big')

    public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())

    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

@pytest.fixture(scope="session")
def integration_test_oauth_client() -> Iterable[IntegrationTestOAuthClient]:
    """
    A testcontainers keycloak fixture which is initialized once per test run.

    Yields an IntegrationTestOAuthClient which contains an oauth client that was created
    for the scope of this test session.

    Yields:
        Iterable[IntegrationTestOAuthClient]: The integration test oauth client.

    """

    # Hardcoded to a port so we dont have to deal with runtime environment value
    # changes, and can simply set it inside pyproject.toml before hand.
    with KeycloakContainer().with_bind_ports(8080, 47005) \
        .with_realm_import_file("./tests/keycloak_integration_realm.json") as keycloak:
        # client = keycloak.get_client()

        # # Create the integration test keycloak realm.
        realm_name = "integration-test-realm"
        # client.create_realm(payload={"realm": realm_name, "enabled": True})

        # client.change_current_realm(realm_name)
        # client.create_client(
        #     payload={
        #         "clientId": OAUTH_CLIENT_ID,
        #         "enabled": True,
        #         "clientAuthenticatorType": "client-secret",
        #         "secret": OAUTH_CLIENT_SECRET,
        #         "protocol": "openid-connect",
        #         "publicClient": False,
        #         "directAccessGrantsEnabled": True,
        #         "serviceAccountsEnabled": True,
        #     }
        # )

        token_url = keycloak.get_url() + f"/realms/{realm_name}/protocol/openid-connect/token"
        jwks_url = keycloak.get_url() + f"/realms/{realm_name}/protocol/openid-connect/certs"

        # Override the OAUTH_TOKEN_ENDPOINT environment variable for the duration of the test session.
        yield IntegrationTestOAuthClient(OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, token_url=token_url, jwks_url=jwks_url)

@pytest.fixture(scope="session")
def integration_test_vtn_client(integration_test_oauth_client: IntegrationTestOAuthClient) -> Iterable[IntegrationTestVTNClient]:
    """A testcontainers openleadr-vtn fixture which is initialized once per test run.

    Yields an IntegrationTestVTNClient which contains the base URL of the VTN being hosted.

    Args:
        integration_test_oauth_client (IntegrationTestOAuthClient): The integration test oauth client.
        This client is used to fetch the public key file from keycloak 

    Yields:
        Iterable[IntegrationTestVTNClient]: The intregration test vtn client.
    """

    # First we retrieve the public key information from the keycloak JWKS.
    jwks_response = requests.get(integration_test_oauth_client.jwks_url)
    jwks_response.raise_for_status()

    response = jwks_response.json()
    pub_key_jwk = response["keys"][1] # Extract the public key from the second key in the list (rs256 pub key by default in keycloak)

    pem_bytes = jwk_to_pem(jwk=pub_key_jwk)
    
    with tempfile.NamedTemporaryFile(delete=True) as temp_pem_file:
        # Write the PEM bytes of the keycloak instance to the temp file.
        temp_pem_file.write(pem_bytes)
        temp_pem_file.flush()

        with Network() as vtn_network:
            # Spin up the postgres DB used by the VTN.
            with PostgresContainer(image="postgres:16", username="openadr", password="openadr", dbname="openadr") \
                .with_network(vtn_network) \
                .with_network_aliases("vtndb") as vtn_db:
                rust_compatible_db_url = vtn_db.get_connection_url(driver=None) \
                    .replace("postgresql", "postgres") \
                    .replace("localhost", "vtndb") \
                    .replace(vtn_db.get_exposed_port(5432), "5432")

                with DockerContainer(image="ghcr.io/openleadr/openleadr-rs:1745824044-94160f7") \
                    .with_exposed_ports(3000) \
                    .with_volume_mapping(host=temp_pem_file.name, container="/keys/pub-sign-key.pem") \
                    .with_env(key="OAUTH_TYPE", value="EXTERNAL") \
                    .with_env(key="OAUTH_VALID_AUDIENCES", value="https://integration.test.elaad.nl") \
                    .with_env(key="OAUTH_KEY_TYPE", value="RSA") \
                    .with_env(key="OAUTH_PEM", value="/keys/pub-sign-key.pem") \
                    .with_env(key="DATABASE_URL", value=rust_compatible_db_url) \
                    .with_env(key="PG_PORT", value=vtn_db.port) \
                    .with_env(key="PG_DB", value="openadr") \
                    .with_env(key="PG_USER", value="openadr") \
                    .with_env(key="PG_PASSWORD", value="openadr") \
                    .with_env(key="PG_TZ", value="Europe/Amsterdam") \
                    .with_env(key="RUST_BACKTRACE", value="full") \
                    .with_env(key="RUST_LOG", value="trace") \
                    .with_network(vtn_network) as vtn_container:
                        # wait_for_logs(vtn_container, "listening on", timeout=30)
                        yield IntegrationTestVTNClient(base_url=f"http://localhost:{vtn_container.get_exposed_port(3000)}")