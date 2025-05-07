"""Contains tests for the factory module."""

from openadr3_client.bl._client import BusinessLogicClient
from openadr3_client.bl.http_factory import BusinessLogicHttpClientFactory


def test_http_bl_client_creates_business_logic_client():
    """Test to validate that the client factory can create a (HTTP) BusinessLogic client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = BusinessLogicHttpClientFactory.create_http_bl_client(vtn_base_url)
    assert isinstance(client, BusinessLogicClient)
