"""Module containing fixtures relevant for testing the authentication module."""

import logging
import os
from collections.abc import Iterable
from pathlib import Path

import jwt
import jwt.algorithms
import pytest
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from testcontainers.keycloak import KeycloakContainer

from openadr3_client.config import OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_TOKEN_ENDPOINT
from tests.openleadr_test_container import OpenLeadrVtnTestContainer

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
            base_url (str): The base URL of the VTN.

        """
        self.vtn_base_url = base_url


class IntegrationTestOAuthClient:
    """
    Class containing an OAUTH client configured for use in integration tests.

    This client is configured inside the keycloak testcontainer and is guaranteed
    to exist for the duration of the integration tests.
    """

    def __init__(self, client_id: str, client_secret: str, token_url: str, public_signing_key_pem_path: str) -> None:
        """
        Initializes the IntegrationTestOAuthClient.

        Args:
            client_id (str): the client id.
            client_secret (str): The client secret.
            token_url (str): The token URL to fetch tokens from.
            public_signing_key_pem_path (str): The path to the public signing key in PEM format.

        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.public_signing_key_pem_path = public_signing_key_pem_path


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
    with (
        KeycloakContainer()
        .with_bind_ports(8080, 47005)
        .with_realm_import_file("./tests/keycloak_integration_realm.json") as keycloak
    ):
        realm_name = "integration-test-realm"
        jwks_url = keycloak.get_url() + f"/realms/{realm_name}/protocol/openid-connect/certs"

        # Retrieve the public key information from the keycloak JWKS.
        jwks_response = requests.get(jwks_url, timeout=10)
        jwks_response.raise_for_status()

        response = jwks_response.json()
        pub_key_jwk = [key for key in response["keys"] if key["alg"] == "RS256"]

        rsa_pub_key = jwt.algorithms.RSAAlgorithm.from_jwk(pub_key_jwk[0])

        if isinstance(rsa_pub_key, RSAPrivateKey):
            exc_msg = "JWK should not contain RSAPrivateKey."
            raise TypeError(exc_msg)

        temp_pem_file_path = Path(__file__).parent / "temp_pem_file.pem"

        with temp_pem_file_path.open("wb") as temp_pem_file:
            try:
                # Write the public key PEM bytes of the keycloak instance to the temp file.
                temp_pem_file.write(
                    rsa_pub_key.public_bytes(
                        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )
                temp_pem_file.flush()
                temp_pem_file.close()

                yield IntegrationTestOAuthClient(
                    OAUTH_CLIENT_ID,
                    OAUTH_CLIENT_SECRET,
                    token_url=OAUTH_TOKEN_ENDPOINT,
                    public_signing_key_pem_path=temp_pem_file.name,
                )

            finally:
                os.remove(temp_pem_file.name)  # noqa: PTH107


@pytest.fixture(scope="session")
def integration_test_vtn_client(
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> Iterable[IntegrationTestVTNClient]:
    """
    A testcontainers openleadr-vtn fixture which is initialized once per test run.

    Yields an IntegrationTestVTNClient which contains the base URL of the VTN being hosted.

    Args:
        integration_test_oauth_client (IntegrationTestOAuthClient): The integration test oauth client.
        This client is used to fetch the public key file from keycloak

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    with OpenLeadrVtnTestContainer(
        external_oauth_signing_key_pem_path=integration_test_oauth_client.public_signing_key_pem_path,
        oauth_valid_audiences="https://integration.test.elaad.nl,",
        openleadr_rs_image="ghcr.io/openleadr/openleadr-rs:1745824044-94160f7",
    ) as vtn_container:
        yield IntegrationTestVTNClient(base_url=vtn_container.get_base_url())
