# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Module containing fixtures relevant for testing the authentication module."""

import logging
import os
from collections.abc import Callable, Generator, Iterable
from typing import Any, cast

import jwt
import pytest
from testcontainers.core.network import Network
from testcontainers.keycloak import KeycloakContainer

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client.plugin import ValidatorPluginRegistry
from tests.openadr310_vtn_test_container import OpenADR310RefImplementationVtnTestContainer
from tests.openleadr_test_container import OpenAdr301VtnTestContainer, OpenAdr310VtnTestContainer

# Set up logging for the testcontainers package
logging.basicConfig(level=logging.DEBUG)

_CONTAINER_LOG_TAIL_LINES = 15
_FAILURE_LOG_SOURCES: list[tuple[str, Callable[[int], list[str]]]] = []


def _dump_container_logs_for_failure(*, failing_test: str) -> None:
    """Dump captured container logs into pytest's captured Python logs (on failure only)."""
    container_logger = logging.getLogger("tests.container_logs")

    if not _FAILURE_LOG_SOURCES:
        return

    container_logger.error("[container_logs] === Container logs for failing test: %s ===", failing_test)
    for name, tail_fn in _FAILURE_LOG_SOURCES:
        try:
            lines = tail_fn(_CONTAINER_LOG_TAIL_LINES)
        except Exception:
            container_logger.exception("[container_logs] %s: failed to retrieve logs", name)
            continue

        if not lines:
            container_logger.error("[container_logs] %s: <no logs captured>", name)
            continue

        container_logger.error("[container_logs] %s: last %d lines", name, len(lines))
        for line in lines:
            container_logger.error("[container_logs] %s | %s", name, line)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]) -> Generator[None, None, None]:
    """Expose test outcome info to fixtures via `request.node.rep_*`."""
    del call
    outcome = yield
    rep = cast("Any", outcome).get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def _dump_container_logs_on_failure(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """On test failure, dump tail logs from registered containers via `logging`."""
    yield

    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call = getattr(request.node, "rep_call", None)
    failed = bool(getattr(rep_setup, "failed", False) or getattr(rep_call, "failed", False))
    if failed:
        _dump_container_logs_for_failure(failing_test=request.node.nodeid)


KEYCLOAK_REALM_NAME = "integration-test-realm"

# Keycloak OAuth test clients (from `tests/keycloak_integration_realm.json`)
KEYCLOAK_BL_CLIENT_ID = "test-client-id"
KEYCLOAK_BL_CLIENT_SECRET = "my-client-secret"
KEYCLOAK_VEN1_CLIENT_ID = "test-ven-1"
KEYCLOAK_VEN2_CLIENT_ID = "test-ven-2"
KEYCLOAK_VEN_CLIENT_SECRET = "my-client-secret"

KEYCLOAK_INTERNAL_BASE_URL = f"http://keycloak:8080/realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect"
KEYCLOAK_INTERNAL_TOKEN_URL = f"{KEYCLOAK_INTERNAL_BASE_URL}/token"
KEYCLOAK_INTERNAL_JWKS_URL = f"{KEYCLOAK_INTERNAL_BASE_URL}/certs"

# Scopes expected by OpenLEADR-rs (used when testing against OpenLEADR-rs VTNs).
# These match the scope strings parsed by OpenLEADR-rs in `openleadr-vtn/src/jwt.rs`.
OPENLEADR_RS_BL_SCOPES = [
    "read_all",
    "write_programs",
    "write_events",
    "write_reports",
    "write_subscriptions",
    "write_vens",
    "write_users",
]
OPENLEADR_RS_VEN_SCOPES = [
    "read_targets",
    "read_ven_objects",
    "write_reports",
    "write_subscriptions",
    "write_vens",
]


@pytest.fixture(scope="session", autouse=True)
def _allow_insecure_http_for_openadr31_tests() -> None:
    """
    Allow HTTP in OpenADR 3.1 integration tests.

    OpenADR 3.1 requires HTTPS, but the OpenLEADR-rs VTN integration test container runs HTTP.
    This opt-in flag keeps production behavior unchanged while allowing local integration testing.
    """
    os.environ.setdefault("OPENADR3_ALLOW_INSECURE_HTTP", "true")
    # Keycloak may add default scopes beyond the ones explicitly requested.
    # oauthlib treats this as a warning by default; relax it for integration tests.
    os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")


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

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
        mqtt_broker_url: str | None = None,
        openadr_client_id: str | None = None,
    ) -> None:
        """
        Initializes the IntegrationTestOAuthClient.

        Args:
            base_url (str): The base URL of the VTN.
            config (OAuthTokenManagerConfig): The OAuth token manager configuration.
            mqtt_broker_url (str | None): The MQTT broker URL to use for communication with the VTN.
            openadr_client_id (str | None): OpenADR clientID to use for association checks (defaults to OAuth client_id).

        """
        self.vtn_base_url = base_url
        self.config = config
        self.mqtt_broker_url = mqtt_broker_url
        # Some VTNs (e.g. OpenLEADR-rs) use the OAuth token `sub` claim as OpenADR clientID.
        # This can differ from the OAuth client_id used for client_credentials.
        self.openadr_client_id = openadr_client_id or config.client_id


def _openadr_client_id_from_oauth(config: OAuthTokenManagerConfig) -> str:
    token = OAuthTokenManager(config).get_access_token()
    # We only need the subject string; signature verification is handled by the VTN itself.
    claims = jwt.decode(token, options={"verify_signature": False})
    sub = claims.get("sub")
    if isinstance(sub, str) and sub:
        return sub
    return config.client_id


class IntegrationTestOAuthClient:
    """
    Class containing an OAUTH client configured for use in integration tests.

    This client is configured inside the keycloak testcontainer and is guaranteed
    to exist for the duration of the integration tests.
    """

    def __init__(self, client_id: str, client_secret: str, token_url: str) -> None:
        """
        Initializes the IntegrationTestOAuthClient.

        Args:
            client_id (str): the client id.
            client_secret (str): The client secret.
            token_url (str): The token URL to fetch tokens from.

        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url


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
def integration_test_oauth_client(integration_test_auth_server: KeycloakContainer) -> IntegrationTestOAuthClient:
    """
    A testcontainers keycloak fixture which is initialized once per test run.

    Yields an IntegrationTestOAuthClient which contains an oauth client that was created
    for the scope of this test session.

    Yields:
        IntegrationTestOAuthClient: The integration test oauth client.

    """
    token_url = integration_test_auth_server.get_url() + f"/realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/token"
    return IntegrationTestOAuthClient(
        client_id=KEYCLOAK_BL_CLIENT_ID,
        client_secret=KEYCLOAK_BL_CLIENT_SECRET,
        token_url=token_url,
    )


@pytest.fixture(scope="session")
def integration_test_openadr301_vtn_client(
    integration_test_docker_network: Network,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> Iterable[IntegrationTestVTNClient]:
    """
    A testcontainers openleadr-vtn (OpenADR 3.0.1) fixture which is initialized once per test run.

    Yields an OpenAdr301VtnTestContainer which contains the base URL of the VTN being hosted.

    Args:
        integration_test_docker_network (Network): The docker network to which the keycloak container will be connected.
        integration_test_oauth_client (IntegrationTestOAuthClient): OAuth client for retrieving access tokens (Keycloak).

    Yields:
        Iterable[OpenAdr301VtnTestContainer]: The integration test vtn client.

    """
    with OpenAdr301VtnTestContainer(
        oauth_jwks_url=KEYCLOAK_INTERNAL_JWKS_URL,
        oauth_valid_audiences="https://integration.test.elaad.nl,",
        oauth_token_url=KEYCLOAK_INTERNAL_TOKEN_URL,
        network=integration_test_docker_network,
    ) as vtn_container:
        _FAILURE_LOG_SOURCES.append(("openleadr-rs-vtn-301", vtn_container.get_vtn_log_tail))
        yield IntegrationTestVTNClient(
            base_url=vtn_container.get_base_url(),
            config=OAuthTokenManagerConfig(
                client_id=integration_test_oauth_client.client_id,
                client_secret=integration_test_oauth_client.client_secret,
                token_url=integration_test_oauth_client.token_url,
                scopes=OPENLEADR_RS_BL_SCOPES,
                audience=None,
            ),
        )


@pytest.fixture(scope="session")
def integration_test_vtn_client(integration_test_openadr301_vtn_client: IntegrationTestVTNClient) -> IntegrationTestVTNClient:
    """
    Backwards-compatible OpenADR 3.0.1 VTN fixture alias.

    The `tests/oadr301/vtn/http/*` suite historically used `integration_test_vtn_client`.
    """
    return integration_test_openadr301_vtn_client


@pytest.fixture(scope="session")
def integration_test_openadr310_vtn_client(
    integration_test_docker_network: Network,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> Iterable[IntegrationTestVTNClient]:
    """
    A testcontainers openleadr-vtn (OpenADR 3.1.0) fixture which is initialized once per test run.

    Yields an OpenAdr310VtnTestContainer which contains the base URL of the VTN being hosted.

    Args:
        integration_test_docker_network (Network): The docker network to which the keycloak container will be connected.
        integration_test_oauth_client (IntegrationTestOAuthClient): OAuth client for retrieving access tokens (Keycloak).

    Yields:
        Iterable[OpenAdr310VtnTestContainer]: The integration test vtn client.

    """
    with OpenAdr310VtnTestContainer(
        oauth_jwks_url=KEYCLOAK_INTERNAL_JWKS_URL,
        oauth_valid_audiences="https://integration.test.elaad.nl,",
        oauth_token_url=KEYCLOAK_INTERNAL_TOKEN_URL,
        network=integration_test_docker_network,
    ) as vtn_container:
        _FAILURE_LOG_SOURCES.append(("openleadr-rs-vtn-310", vtn_container.get_vtn_log_tail))
        yield IntegrationTestVTNClient(
            base_url=vtn_container.get_base_url(),
            config=OAuthTokenManagerConfig(
                client_id=integration_test_oauth_client.client_id,
                client_secret=integration_test_oauth_client.client_secret,
                token_url=integration_test_oauth_client.token_url,
                scopes=OPENLEADR_RS_BL_SCOPES,
                audience=None,
            ),
        )


@pytest.fixture(scope="session")
def integration_test_openadr310_reference_vtn(
    integration_test_docker_network: Network,
) -> Iterable[OpenADR310RefImplementationVtnTestContainer]:
    """
    OpenADR 3.1.0 reference VTN container (temporary dependency).

    This container is only used by the MQTT integration tests that validate VTN-originated MQTT publishes.
    All OpenADR 3.1 HTTP integration tests use OpenLEADR-rs (`integration_test_openadr310_vtn_client`).
    """
    with OpenADR310RefImplementationVtnTestContainer(
        oauth_token_endpoint=KEYCLOAK_INTERNAL_TOKEN_URL,
        oauth_jwks_url=KEYCLOAK_INTERNAL_JWKS_URL,
        network=integration_test_docker_network,
    ) as vtn_container:
        _FAILURE_LOG_SOURCES.append(("oadr310-ref-vtn", vtn_container.get_vtn_log_tail))
        yield vtn_container


@pytest.fixture(scope="session")
def vtn_openadr_310_bl_token(
    integration_test_openadr310_vtn_client: IntegrationTestVTNClient,
) -> IntegrationTestVTNClient:
    """
    Returns an integration test VTN client instance which is configured to have a BL token to communicate with the VTN.

    Args:
        integration_test_openadr310_vtn_client (IntegrationTestVTNClient): OpenLEADR-rs VTN client (HTTP tests).

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    return integration_test_openadr310_vtn_client


@pytest.fixture(scope="session")
def vtn_openadr_310_ven_token(
    integration_test_openadr310_vtn_client: IntegrationTestVTNClient,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> IntegrationTestVTNClient:
    """
    Returns an integration test VTN client instance which is configured to have a VEN token to communicate with the VTN.

    Args:
        integration_test_openadr310_vtn_client (IntegrationTestVTNClient): OpenLEADR-rs VTN client (HTTP tests).
        integration_test_oauth_client (IntegrationTestOAuthClient): OAuth client for retrieving access tokens (Keycloak).

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    config = OAuthTokenManagerConfig(
        client_id=KEYCLOAK_VEN1_CLIENT_ID,
        client_secret=KEYCLOAK_VEN_CLIENT_SECRET,
        token_url=integration_test_oauth_client.token_url,
        scopes=OPENLEADR_RS_VEN_SCOPES,
        audience=None,
    )
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_vtn_client.vtn_base_url,
        config=config,
        openadr_client_id=_openadr_client_id_from_oauth(config),
    )


@pytest.fixture(scope="session")
def vtn_openadr_310_ven2_token(
    integration_test_openadr310_vtn_client: IntegrationTestVTNClient,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> IntegrationTestVTNClient:
    """
    Returns an integration test VTN client instance which is configured to have a VEN token to communicate with the VTN.

    Args:
        integration_test_openadr310_vtn_client (IntegrationTestVTNClient): OpenLEADR-rs VTN client (HTTP tests).
        integration_test_oauth_client (IntegrationTestOAuthClient): OAuth client for retrieving access tokens (Keycloak).

    Yields:
        Iterable[IntegrationTestVTNClient]: The integration test vtn client.

    """
    config = OAuthTokenManagerConfig(
        client_id=KEYCLOAK_VEN2_CLIENT_ID,
        client_secret=KEYCLOAK_VEN_CLIENT_SECRET,
        token_url=integration_test_oauth_client.token_url,
        scopes=OPENLEADR_RS_VEN_SCOPES,
        audience=None,
    )
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_vtn_client.vtn_base_url,
        config=config,
        openadr_client_id=_openadr_client_id_from_oauth(config),
    )


@pytest.fixture(scope="session")
def vtn_openadr_310_bl_token_reference(
    integration_test_openadr310_reference_vtn: OpenADR310RefImplementationVtnTestContainer,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> IntegrationTestVTNClient:
    """Reference-VTN backed BL token client (used by MQTT publish tests only)."""
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_reference_vtn.get_base_url(),
        config=OAuthTokenManagerConfig(
            client_id=integration_test_oauth_client.client_id,
            client_secret=integration_test_oauth_client.client_secret,
            token_url=integration_test_oauth_client.token_url,
            scopes=None,
            audience=None,
        ),
        mqtt_broker_url=integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url(),
    )


@pytest.fixture(scope="session")
def vtn_openadr_310_ven_token_reference(
    integration_test_openadr310_reference_vtn: OpenADR310RefImplementationVtnTestContainer,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> IntegrationTestVTNClient:
    """Reference-VTN backed VEN token client (used by MQTT publish tests only)."""
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_reference_vtn.get_base_url(),
        config=OAuthTokenManagerConfig(
            client_id=KEYCLOAK_VEN1_CLIENT_ID,
            client_secret=KEYCLOAK_VEN_CLIENT_SECRET,
            token_url=integration_test_oauth_client.token_url,
            scopes=None,
            audience=None,
        ),
        mqtt_broker_url=integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url(),
    )


@pytest.fixture(scope="session")
def vtn_openadr_310_ven2_token_reference(
    integration_test_openadr310_reference_vtn: OpenADR310RefImplementationVtnTestContainer,
    integration_test_oauth_client: IntegrationTestOAuthClient,
) -> IntegrationTestVTNClient:
    """Reference-VTN backed VEN2 token client (used by MQTT publish tests only)."""
    return IntegrationTestVTNClient(
        base_url=integration_test_openadr310_reference_vtn.get_base_url(),
        config=OAuthTokenManagerConfig(
            client_id=KEYCLOAK_VEN2_CLIENT_ID,
            client_secret=KEYCLOAK_VEN_CLIENT_SECRET,
            token_url=integration_test_oauth_client.token_url,
            scopes=None,
            audience=None,
        ),
        mqtt_broker_url=integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url(),
    )
