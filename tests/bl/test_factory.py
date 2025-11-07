"""Contains tests for the factory module."""

import os

from openadr3_client.bl._client import BusinessLogicClient
from openadr3_client.bl.http_factory import BusinessLogicHttpClientFactory

OAUTH_TOKEN_ENDPOINT = os.getenv("OAUTH_TOKEN_ENDPOINT", "dummy")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "dummy")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "dummy")


def test_http_bl_client_creates_business_logic_client():
    """Test to validate that the client factory can create a (HTTP) BusinessLogic client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = BusinessLogicHttpClientFactory.create_http_bl_client(vtn_base_url, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_TOKEN_ENDPOINT)
    assert isinstance(client, BusinessLogicClient)
