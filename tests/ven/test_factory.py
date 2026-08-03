# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains tests for the factory module."""

import os

import pytest

from openadr3_client._common.http.authenticated_session import (
    HTTPSOnlySession,
    UnauthenticatedSession,
    _BearerAuth,
)
from openadr3_client.ven._client import BaseVirtualEndNodeClient
from openadr3_client.ven.http_factory import VirtualEndNodeHttpClientFactory
from openadr3_client.version import OADRVersion

OAUTH_TOKEN_ENDPOINT = os.getenv("OAUTH_TOKEN_ENDPOINT", "dummy")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "dummy")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "dummy")


def test_http_ven_client_creates_ven_logic_client_oadr301():
    """Test to validate that the client factory can create a (HTTP) VEN client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = VirtualEndNodeHttpClientFactory.create_http_ven_client(
        vtn_base_url=vtn_base_url,
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        token_url=OAUTH_TOKEN_ENDPOINT,
        version=OADRVersion.OADR_301,
    )
    assert isinstance(client, BaseVirtualEndNodeClient)


def test_http_ven_client_creates_ven_logic_client_oadr310():
    """Test to validate that the client factory can create a (HTTP) VEN client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = VirtualEndNodeHttpClientFactory.create_http_ven_client(
        vtn_base_url=vtn_base_url,
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        token_url=OAUTH_TOKEN_ENDPOINT,
        version=OADRVersion.OADR_310,
    )
    assert isinstance(client, BaseVirtualEndNodeClient)
    # An authenticated client attaches a bearer token to its requests.
    assert isinstance(client.programs.session.auth, _BearerAuth)  # type: ignore[attr-defined]


def test_http_ven_client_creates_anonymous_client_oadr301():
    """Test that the anonymous factory creates an unauthenticated OpenADR 3.0.1 VEN client."""
    client = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(
        vtn_base_url="https://elaad.nl/vtn",
        version=OADRVersion.OADR_301,
    )
    assert isinstance(client, BaseVirtualEndNodeClient)
    session = client.programs.session  # type: ignore[attr-defined]
    # An anonymous 3.0.1 client uses an unauthenticated session and attaches no authentication.
    assert isinstance(session, UnauthenticatedSession)
    assert session.auth is None


def test_http_ven_client_creates_anonymous_client_oadr310():
    """Test that the anonymous factory creates an unauthenticated OpenADR 3.1.0 VEN client."""
    client = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(
        vtn_base_url="https://elaad.nl/vtn",
        version=OADRVersion.OADR_310,
    )
    assert isinstance(client, BaseVirtualEndNodeClient)
    session = client.programs.session  # type: ignore[attr-defined]
    # An anonymous 3.1.0 client uses an HTTPS-only session (HTTPS enforcement preserved) with no auth.
    # Exact-type check: the authenticated 3.1.0 session subclasses HTTPSOnlySession, so isinstance alone
    # would not distinguish it from an anonymous one.
    assert type(session) is HTTPSOnlySession
    assert session.auth is None


def test_anonymous_ven_client_oadr310_enforces_https():
    """Test that an anonymous 3.1.0 VEN client rejects plain HTTP requests (HTTPS enforcement preserved)."""
    client = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(
        vtn_base_url="http://insecure.example/vtn",
        version=OADRVersion.OADR_310,
    )
    with pytest.raises(ValueError, match="HTTP requests are not allowed"):
        client.programs.get_programs(target=None, pagination=None)  # type: ignore[attr-defined]


def test_anonymous_ven_client_oadr310_wires_tls_verification():
    """Test that verify_vtn_tls_certificate reaches the anonymous 3.1.0 session's verify attribute."""
    client_disabled = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(
        vtn_base_url="https://elaad.nl/vtn",
        verify_vtn_tls_certificate=False,
        version=OADRVersion.OADR_310,
    )
    assert client_disabled.programs.session.verify is False  # type: ignore[attr-defined]

    ca_bundle = "/etc/ssl/custom-ca.pem"
    client_custom_ca = VirtualEndNodeHttpClientFactory.create_anonymous_http_ven_client(
        vtn_base_url="https://elaad.nl/vtn",
        verify_vtn_tls_certificate=ca_bundle,
        version=OADRVersion.OADR_310,
    )
    assert client_custom_ca.programs.session.verify == ca_bundle  # type: ignore[attr-defined]
