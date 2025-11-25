"""Contains tests for the factory module."""

import os

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
