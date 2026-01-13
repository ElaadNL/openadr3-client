# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains tests for the factory module."""

import os

from openadr3_client.bl._client import BaseBusinessLogicClient
from openadr3_client.bl.http_factory import BusinessLogicHttpClientFactory
from openadr3_client.version import OADRVersion

OAUTH_TOKEN_ENDPOINT = os.getenv("OAUTH_TOKEN_ENDPOINT", "dummy")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "dummy")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "dummy")


def test_http_bl_client_creates_business_logic_client_oadr301():
    """Test to validate that the client factory can create a (HTTP) BusinessLogic client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = BusinessLogicHttpClientFactory.create_http_bl_client(
        vtn_base_url=vtn_base_url,
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        token_url=OAUTH_TOKEN_ENDPOINT,
        version=OADRVersion.OADR_301,
    )
    assert isinstance(client, BaseBusinessLogicClient)


def test_http_bl_client_creates_business_logic_client_oadr310():
    """Test to validate that the client factory can create a (HTTP) BusinessLogic client."""
    vtn_base_url = "https://elaad.nl/vtn"
    client = BusinessLogicHttpClientFactory.create_http_bl_client(
        vtn_base_url=vtn_base_url,
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        token_url=OAUTH_TOKEN_ENDPOINT,
        version=OADRVersion.OADR_310,
    )
    assert isinstance(client, BaseBusinessLogicClient)
