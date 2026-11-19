# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Tests that every HTTP request made by the client is bounded by a timeout (issue #149)."""

import socket
import time
from collections.abc import Callable, Iterator
from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError
from requests.adapters import HTTPAdapter

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client._common.http.authenticated_session import (
    BearerAuthenticatedSession,
    HTTPSOnlySession,
    UnauthenticatedSession,
    _BearerAuthenticatedHttpsOnlySession,
    _TimeoutSession,
)
from openadr3_client._common.http.timeout import DEFAULT_HTTP_TIMEOUT, HttpTimeout, validate_http_timeout
from openadr3_client.bl.http_factory import BusinessLogicHttpClientFactory
from openadr3_client.extensions.resource_group.factory import ResourceGroupClientFactory
from openadr3_client.ven.http_factory import VirtualEndNodeHttpClientFactory
from openadr3_client.version import OADRVersion

VTN_URL = "https://vtn.example.com"
TOKEN_URL = "https://auth.example.com/token"
CUSTOM_TIMEOUT: HttpTimeout = (1.5, 7.0)
TOKEN_RESPONSE = {"access_token": "token", "expires_in": 60}


def _token_config(timeout: object = DEFAULT_HTTP_TIMEOUT) -> OAuthTokenManagerConfig:
    return OAuthTokenManagerConfig(client_id="id", client_secret="secret", token_url=TOKEN_URL, scopes=None, audience=None, timeout=timeout)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("timeout", "expected"), [(30, 30.0), (0.5, 0.5), ((3, 27), (3.0, 27.0)), ((0.1, 1.5), (0.1, 1.5))])
def test_validate_accepts_positive_numbers_and_tuples(timeout: HttpTimeout, expected: HttpTimeout) -> None:
    """Positive numbers and (connect, read) tuples are accepted and normalized to floats."""
    assert validate_http_timeout(timeout) == expected


def test_validate_rejects_none() -> None:
    """None would wait indefinitely, so it is rejected."""
    with pytest.raises(TypeError, match="must not be None"):
        validate_http_timeout(None)  # type: ignore[arg-type]


@pytest.mark.parametrize("timeout", [0, -1, 0.0, float("inf"), float("nan"), (0, 5), (5, -1), (5,), (1, 2, 3)])
def test_validate_rejects_invalid_values(timeout: object) -> None:
    """Zero, negative, non-finite values and malformed tuples are rejected."""
    with pytest.raises(ValueError, match="timeout"):
        validate_http_timeout(timeout)  # type: ignore[arg-type]


@pytest.mark.parametrize("timeout", [True, "30", (None, 5), (5, None), [3, 27]])
def test_validate_rejects_invalid_types(timeout: object) -> None:
    """Booleans, strings, lists and tuples containing None are rejected."""
    with pytest.raises(TypeError):
        validate_http_timeout(timeout)  # type: ignore[arg-type]


def test_factory_rejects_none_timeout() -> None:
    """Client factories reject a None timeout."""
    with pytest.raises(TypeError, match="must not be None"):
        VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(vtn_base_url=VTN_URL, version=OADRVersion.OADR_310, timeout=None)  # type: ignore[arg-type]


def test_token_manager_rejects_none_timeout() -> None:
    """The token manager rejects a None timeout."""
    with pytest.raises(TypeError, match="must not be None"):
        OAuthTokenManager(_token_config(timeout=None))


# ---------------------------------------------------------------------------
# Every session the client creates applies the timeout to every request
# ---------------------------------------------------------------------------


@pytest.fixture
def sent_timeouts() -> Iterator[list[object]]:
    """Capture the timeout of every request that reaches the transport layer, without touching the network."""
    timeouts: list[object] = []

    def fake_send(_self: HTTPAdapter, request: requests.PreparedRequest, **kwargs: object) -> requests.Response:
        timeouts.append(kwargs.get("timeout"))
        response = requests.Response()
        response.status_code = 200
        response._content = b"{}"
        response.request = request
        response.url = request.url or ""
        return response

    with patch.object(HTTPAdapter, "send", fake_send):
        yield timeouts


def _token_manager_mock() -> MagicMock:
    return MagicMock(get_access_token=MagicMock(return_value="token"))


SESSION_BUILDERS: dict[str, Callable[[HttpTimeout], _TimeoutSession]] = {
    "UnauthenticatedSession": lambda t: UnauthenticatedSession(timeout=t),
    "HTTPSOnlySession": lambda t: HTTPSOnlySession(timeout=t),
    "BearerAuthenticatedSession": lambda t: BearerAuthenticatedSession(_token_manager_mock(), timeout=t),
    "_BearerAuthenticatedHttpsOnlySession": lambda t: _BearerAuthenticatedHttpsOnlySession(_token_manager_mock(), timeout=t),
}


@pytest.mark.parametrize("build", SESSION_BUILDERS.values(), ids=SESSION_BUILDERS.keys())
@pytest.mark.parametrize("method", ["get", "post", "put", "delete"])
def test_session_applies_timeout_to_every_method(build: Callable[[HttpTimeout], _TimeoutSession], method: str, sent_timeouts: list[object]) -> None:
    """Every session type sends its configured timeout with every HTTP method."""
    session = build(CUSTOM_TIMEOUT)
    getattr(session, method)(f"{VTN_URL}/programs")
    assert sent_timeouts == [CUSTOM_TIMEOUT]


@pytest.mark.parametrize("session_class", [UnauthenticatedSession, HTTPSOnlySession])
def test_session_defaults_to_default_timeout(session_class: type[_TimeoutSession], sent_timeouts: list[object]) -> None:
    """A session created without a timeout uses the default timeout."""
    session_class().get(f"{VTN_URL}/programs")
    assert sent_timeouts == [DEFAULT_HTTP_TIMEOUT]


def test_session_replaces_explicit_none_timeout(sent_timeouts: list[object]) -> None:
    """A per-request timeout=None would wait indefinitely, so the session timeout is used instead."""
    UnauthenticatedSession(timeout=CUSTOM_TIMEOUT).get(f"{VTN_URL}/programs", timeout=None)
    assert sent_timeouts == [CUSTOM_TIMEOUT]


def test_session_keeps_explicit_per_request_timeout(sent_timeouts: list[object]) -> None:
    """An explicit per-request timeout takes precedence over the session timeout."""
    UnauthenticatedSession(timeout=CUSTOM_TIMEOUT).get(f"{VTN_URL}/programs", timeout=2)
    assert sent_timeouts == [2]


# ---------------------------------------------------------------------------
# Guard: every interface of every client is wired to the configured timeout.
# Interfaces are discovered from the client instances, so new interfaces are covered automatically.
# ---------------------------------------------------------------------------


def _interfaces(client: object) -> list[tuple[str, object]]:
    interfaces = [(name, value) for name, value in vars(client).items() if hasattr(value, "session")]
    assert interfaces, f"No HTTP interfaces found on {type(client).__name__}"
    return interfaces


def _clients(timeout: HttpTimeout) -> dict[str, object]:
    clients: dict[str, object] = {}
    for version in OADRVersion:
        clients[f"ven-auth-{version.name}"] = VirtualEndNodeHttpClientFactory.create_http_ven_client(
            vtn_base_url=VTN_URL, client_id="id", client_secret="secret", token_url=TOKEN_URL, version=version, timeout=timeout
        )
        clients[f"ven-anon-{version.name}"] = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(vtn_base_url=VTN_URL, version=version, timeout=timeout)
        clients[f"bl-auth-{version.name}"] = BusinessLogicHttpClientFactory.create_http_bl_client(
            vtn_base_url=VTN_URL, client_id="id", client_secret="secret", token_url=TOKEN_URL, version=version, timeout=timeout
        )
        clients[f"bl-anon-{version.name}"] = BusinessLogicHttpClientFactory.create_anonymous_http_bl_client(vtn_base_url=VTN_URL, version=version, timeout=timeout)
    return clients


def _assert_session_timeout(session: object, timeout: HttpTimeout, where: str) -> None:
    assert isinstance(session, _TimeoutSession), f"{where} uses {type(session).__name__}, which does not enforce a timeout"
    assert session.timeout == timeout, where
    token_manager = getattr(session.auth, "_token_manager", None)
    if token_manager is not None:
        assert token_manager.timeout == timeout, f"{where} token manager"


@pytest.mark.parametrize("timeout", [DEFAULT_HTTP_TIMEOUT, CUSTOM_TIMEOUT])
def test_all_client_interfaces_use_configured_timeout(timeout: HttpTimeout) -> None:
    """Every interface of every BL and VEN client (both versions, authenticated and anonymous) uses the configured timeout."""
    for client_name, client in _clients(timeout).items():
        for name, interface in _interfaces(client):
            _assert_session_timeout(interface.session, timeout, f"{client_name}.{name}")  # type: ignore[attr-defined]


def test_client_factories_default_to_default_timeout() -> None:
    """A client created without a timeout uses the default timeout."""
    client = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(vtn_base_url=VTN_URL, version=OADRVersion.OADR_310)
    for name, interface in _interfaces(client):
        _assert_session_timeout(interface.session, DEFAULT_HTTP_TIMEOUT, name)  # type: ignore[attr-defined]


@pytest.mark.parametrize("factory", [ResourceGroupClientFactory.create_bl_client, ResourceGroupClientFactory.create_ven_client])
def test_resource_group_clients_use_configured_timeout(factory: Callable[..., object]) -> None:
    """Resource group clients and their token managers use the configured timeout."""
    client = factory(vtn_base_url=VTN_URL, client_id="id", client_secret="secret", token_url=TOKEN_URL, timeout=CUSTOM_TIMEOUT)
    _assert_session_timeout(client.session, CUSTOM_TIMEOUT, "resource groups")  # type: ignore[attr-defined]


def test_token_url_discovery_uses_configured_timeout(sent_timeouts: list[object]) -> None:
    """The OpenADR 3.1.0 discovery request, made while building the client, is bounded by the timeout too."""
    # The fake {} response is not valid auth server info, so building the client fails after the discovery request.
    with pytest.raises(ValidationError):
        VirtualEndNodeHttpClientFactory.create_http_ven_client(
            vtn_base_url=VTN_URL, client_id="id", client_secret="secret", token_url=None, version=OADRVersion.OADR_310, timeout=CUSTOM_TIMEOUT
        )
    assert sent_timeouts == [CUSTOM_TIMEOUT]


# ---------------------------------------------------------------------------
# Token endpoint
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("configured", "expected"), [(CUSTOM_TIMEOUT, CUSTOM_TIMEOUT), (DEFAULT_HTTP_TIMEOUT, DEFAULT_HTTP_TIMEOUT)])
def test_token_manager_passes_timeout_to_token_request(configured: HttpTimeout, expected: HttpTimeout) -> None:
    """The token request is sent with the configured timeout, as requests_oauthlib defaults to waiting indefinitely."""
    manager = OAuthTokenManager(_token_config(timeout=configured))
    with patch.object(manager.oauth, "fetch_token", return_value=TOKEN_RESPONSE) as fetch_token:
        assert manager.get_access_token() == "token"
    assert fetch_token.call_args.kwargs["timeout"] == expected


# ---------------------------------------------------------------------------
# Behaviour against a server that accepts connections but never responds
# ---------------------------------------------------------------------------


@pytest.fixture
def unresponsive_server() -> Iterator[str]:
    """A TCP server whose kernel completes the handshake, but which never sends a response."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        server.listen(8)
        host, port = server.getsockname()
        yield f"http://{host}:{port}"


def test_vtn_request_times_out_on_unresponsive_server(unresponsive_server: str) -> None:
    """A VTN request to a server that never responds raises a timeout instead of blocking forever."""
    client = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(
        vtn_base_url=unresponsive_server, version=OADRVersion.OADR_310, allow_insecure_http=True, timeout=0.5
    )
    start = time.monotonic()
    with pytest.raises(requests.exceptions.ReadTimeout):
        client.programs.get_programs(target=None, pagination=None)  # type: ignore[attr-defined]
    assert time.monotonic() - start < 5


def test_token_request_times_out_on_unresponsive_server(unresponsive_server: str) -> None:
    """A token request to a server that never responds raises a timeout instead of blocking forever."""
    # OAUTHLIB_INSECURE_TRANSPORT=1 is set for the test run (pyproject.toml), which allows the http:// token URL.
    config = OAuthTokenManagerConfig(client_id="id", client_secret="secret", token_url=f"{unresponsive_server}/token", scopes=None, audience=None, timeout=0.5)
    start = time.monotonic()
    with pytest.raises(requests.exceptions.ReadTimeout):
        OAuthTokenManager(config).get_access_token()
    assert time.monotonic() - start < 5
