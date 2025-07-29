"""Contains tests for the factory module."""

import os

from openadr3_client.ven._client import VirtualEndNodeClient
from openadr3_client.ven.http_factory import VirtualEndNodeHttpClientFactory

OAUTH_TOKEN_ENDPOINT = os.getenv("OAUTH_TOKEN_ENDPOINT")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")


def test_http_ven_client_creates_ven_logic_client():
    """Test to validate that the client factory can create a (HTTP) VEN client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = VirtualEndNodeHttpClientFactory.create_http_ven_client(
        vtn_base_url,
        OAUTH_CLIENT_ID,
        OAUTH_CLIENT_SECRET,
        OAUTH_TOKEN_ENDPOINT,
    )
    assert isinstance(client, VirtualEndNodeClient)
