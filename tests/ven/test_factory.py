"""Contains tests for the factory module."""

from openadr3_client.ven._client import VirtualEndNodeClient
from openadr3_client.ven.http_factory import VirtualEndNodeHttpClientFactory


def test_http_ven_client_creates_ven_logic_client():
    """Test to validate that the client factory can create a (HTTP) VEN client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = VirtualEndNodeHttpClientFactory.create_http_ven_client(vtn_base_url)
    assert isinstance(client, VirtualEndNodeClient)
