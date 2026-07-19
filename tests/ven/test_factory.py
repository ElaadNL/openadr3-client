# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains tests for the factory module."""

import os

import pytest

from openadr3_client._common.http.authenticated_session import _BearerAuth
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


@pytest.mark.parametrize("version", [OADRVersion.OADR_301, OADRVersion.OADR_310])
def test_http_ven_client_creates_anonymous_client(version: OADRVersion):
    """Test that omitting the client credentials creates an anonymous (unauthenticated) VEN client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = VirtualEndNodeHttpClientFactory.create_http_ven_client(
        vtn_base_url=vtn_base_url,
        version=version,
    )
    assert isinstance(client, BaseVirtualEndNodeClient)
    # An anonymous client does not attach any authentication to its requests.
    assert client.programs.session.auth is None  # type: ignore[attr-defined]


def test_http_ven_client_partial_credentials_raises():
    """Test that providing only one of client_id/client_secret raises a ValueError."""
    with pytest.raises(ValueError, match="Both client_id and client_secret"):
        VirtualEndNodeHttpClientFactory.create_http_ven_client(
            vtn_base_url="https://elaad.nl/vtn",
            client_id=OAUTH_CLIENT_ID,
            token_url=OAUTH_TOKEN_ENDPOINT,
            version=OADRVersion.OADR_310,
        )
