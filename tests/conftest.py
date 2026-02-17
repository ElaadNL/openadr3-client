# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Module containing fixtures relevant for testing the authentication module."""

import logging
import os
from collections.abc import Generator, Iterable
from pathlib import Path

import jwt
import jwt.algorithms
import pytest
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from testcontainers.core.network import Network
from testcontainers.keycloak import KeycloakContainer

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.plugin import ValidatorPluginRegistry
from tests.openadr310_vtn_test_container import OpenADR310VtnTestContainer
from tests.openleadr_test_container import OpenLeadrVtnTestContainer

# Set up logging for the testcontainers package
logging.basicConfig(level=logging.DEBUG)

OAUTH_TOKEN_ENDPOINT = os.getenv("OAUTH_TOKEN_ENDPOINT")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")


@pytest.fixture(autouse=True)
def _clear_validator_plugins() -> Generator[None, None, None]:
    """
    Ensure plugin-based validators don't leak between tests.

    The `ValidatorPluginRegistry` is global state used by `ValidatableModel`. Some tests (and doctests)
    register custom validators; without cleanup, those validators can affect unrelated tests.
    """
    try:
        yield
    finally:
        ValidatorPluginRegistry.clear_plugins()


class IntegrationTestVTNClient:
    """
    Class containing an OpenADR3 VTN client configured for use in integration tests.

    This client is configured as a generic docker testcontainer and is guaranteed
    to exist for the duration of the integration tests.
    """

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, mqtt_broker_url: str | None = None) -> None:
        """
        Initializes the IntegrationTestOAuthClient.

        Args:
            base_url (str): The base URL of the VTN.
            config (OAuthTokenManagerConfig): The OAuth token manager configuration.
            mqtt_broker_url (str | None): The MQTT broker URL to use for communication with the VTN.

        """
        self.vtn_base_url = base_url
        self.config = config
        self.mqtt_broker_url = mqtt_broker_url


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
def integration_test_docker_network() -> Iterable[Network]:
    """
    A testcontainers docker network fixture which is initialized once per test run.

    Yields:
        Iterable[Network]: The docker network.

    """
    with Network() as network:
        yield network


@pytest.fixture(scope="session")
def integration_test_auth_server(integration_test_docker_network: Network) -> Iterable[KeycloakContainer]:
    """
    A testcontainers keycloak fixture which is initialized once per test run.

    Args:
        integration_test_docker_network (Network): The docker network to which the keycloak container will be connected.

    Yields:
        Iterable[KeycloakContainer]: The keycloak container.

    """
    # Hardcoded to a port so we dont have to deal with runtime environment value
    # changes, and can simply set it inside pyproject.toml before hand.
    with (
        KeycloakContainer()
        .with_network(integration_test_docker_network)
        .with_network_aliases("keycloak")
        .with_bind_ports(8080, 47005)
        .with_realm_import_file("./tests/keycloak_integration_realm.json") as keycloak
    ):
        yield keycloak


@pytest.fixture(scope="session")
def integration_test_oauth_client(integration_test_auth_server: KeycloakContainer) -> Iterable[IntegrationTestOAuthClient]:
    """
    A testcontainers keycloak fixture which is initialized once per test run.

    Yields an IntegrationTestOAuthClient which contains an oauth client that was created
    for the scope of this test session.

    Yields:
        Iterable[IntegrationTestOAuthClient]: The integration test oauth client.

    """
    # Hardcoded to a port so we dont have to deal with runtime environment value
    # changes, and can simply set it inside pyproject.toml before hand.
    realm_name = "integration-test-realm"
    jwks_url = integration_test_auth_server.get_url() + f"/realms/{realm_name}/protocol/openid-connect/certs"

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
            temp_pem_file.write(rsa_pub_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo))
            temp_pem_file.flush()
            temp_pem_file.close()

            yield IntegrationTestOAuthClient(
                OAUTH_CLIENT_ID or "",
                OAUTH_CLIENT_SECRET or "",
                token_url=OAUTH_TOKEN_ENDPOINT or "",
                public_signing_key_pem_path=temp_pem_file.name,
            )

        finally:
            os.remove(temp_pem_file.name)  # noqa: PTH107


@pytest.fixture(scope="session")
def integration_test_vtn_client(
    integration_test_docker_network: Network,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> Iterable[IntegrationTestVTNClient]:
    """
    A testcontainers openleadr-vtn (OpenADR 3.0.1) fixture which is initialized once per test run.

    Yields an IntegrationTestVTNClient which contains the base URL of the VTN being hosted.

    Args:
        integration_test_docker_network (Network): The docker network to which the keycloak container will be connected.
        integration_test_oauth_client (IntegrationTestOAuthClient): The integration test oauth client.
        This client is used to fetch the public key file from keycloak

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    with OpenLeadrVtnTestContainer(
        external_oauth_signing_key_pem_path=integration_test_oauth_client.public_signing_key_pem_path,
        oauth_valid_audiences="https://integration.test.elaad.nl,",
        openleadr_rs_image="ghcr.io/openleadr/openleadr-rs:0.1.2",
        network=integration_test_docker_network,
    ) as vtn_container:
        yield IntegrationTestVTNClient(
            base_url=vtn_container.get_base_url(),
            config=OAuthTokenManagerConfig(
                client_id=OAUTH_CLIENT_ID or "",
                client_secret=OAUTH_CLIENT_SECRET or "",
                token_url=OAUTH_TOKEN_ENDPOINT or "",
                scopes=None,
                audience=None,
            ),
        )


@pytest.fixture(scope="session")
def integration_test_openadr310_reference_vtn(
    integration_test_auth_server: KeycloakContainer, integration_test_docker_network: Network
) -> Iterable[OpenADR310VtnTestContainer]:
    """
    A testcontainers OpenADR 3.1 reference VTN (without MQTT broker) fixture which is initialized once per test run.

    Args:
        integration_test_auth_server (KeycloakContainer): The keycloak container.
        integration_test_docker_network (Network): The docker network to which the keycloak container will be connected.

    Yields:
        Iterable[OpenADR310VtnTestContainer]: The OpenADR 3.1 reference VTN container.

    """
    realm_name = "integration-test-realm"
    jwks_url = "http://keycloak:" + f"{integration_test_auth_server.port!s}/realms/{realm_name}/protocol/openid-connect/certs"
    with OpenADR310VtnTestContainer(
        oauth_token_endpoint=OAUTH_TOKEN_ENDPOINT or "",
        oauth_jwks_url=jwks_url,
        network=integration_test_docker_network,
    ) as vtn_container:
        yield vtn_container


@pytest.fixture(scope="session")
def vtn_openadr_310_bl_token(
    integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer,
) -> IntegrationTestVTNClient:
    """
    Returns an integration test VTN client instance which is configured to have a BL token to communicate with the VTN.

    Args:
        integration_test_openadr310_reference_vtn (OpenADR310VtnTestContainer): The openadr 3.1.0 reference VTN container.

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_reference_vtn.get_base_url(),
        config=OAuthTokenManagerConfig(
            client_id=OAUTH_CLIENT_ID or "",
            client_secret=OAUTH_CLIENT_SECRET or "",
            token_url=OAUTH_TOKEN_ENDPOINT or "",
            scopes=None,
            audience=None,
        ),
        mqtt_broker_url=integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url(),
    )


@pytest.fixture(scope="session")
def vtn_openadr_310_ven_token(
    integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer,
) -> IntegrationTestVTNClient:
    """
    Returns an integration test VTN client instance which is configured to have a VEN token to communicate with the VTN.

    Args:
        integration_test_openadr310_reference_vtn (OpenADR310VtnTestContainer): The openadr 3.1.0 reference VTN container.

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_reference_vtn.get_base_url(),
        config=OAuthTokenManagerConfig(
            client_id="test-ven-1",
            client_secret="my-client-secret",
            token_url=OAUTH_TOKEN_ENDPOINT or "",
            scopes=None,
            audience=None,
        ),
        mqtt_broker_url=integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url(),
    )


@pytest.fixture(scope="session")
def vtn_openadr_310_ven2_token(
    integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer,
) -> IntegrationTestVTNClient:
    """
    Returns an integration test VTN client instance which is configured to have a VEN token to communicate with the VTN.

    Args:
        integration_test_openadr310_reference_vtn (OpenADR310VtnTestContainer): The openadr 3.1.0 reference VTN container.

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_reference_vtn.get_base_url(),
        config=OAuthTokenManagerConfig(
            client_id="test-ven-2",
            client_secret="my-client-secret",
            token_url=OAUTH_TOKEN_ENDPOINT or "",
            scopes=None,
            audience=None,
        ),
        mqtt_broker_url=integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url(),
    )
