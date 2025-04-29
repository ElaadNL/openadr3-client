"""Contains tests for the events VTN module."""

import pytest
from requests import HTTPError
from openadr3_client._vtn.http.events import EventsHttpInterface
from tests.conftest import IntegrationTestVTNClient


def test_get_events_unknown_program_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events from a VTN with an unknown program raises an exception."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)
    
    with pytest.raises(HTTPError):
        _ = interface.get_events(target=None, pagination=None, program_id="fake-program")

def test_get_events_no_events_in_vtn(integration_test_vtn_client: IntegrationTestVTNClient) -> None:
    """Test to validate that getting events from a VTN without any events returns an empty list."""
    interface = EventsHttpInterface(base_url=integration_test_vtn_client.vtn_base_url)

    response = interface.get_events(target=None, pagination=None, program_id=None)

    assert len(response) == 1, "no events should be stored in VTN."
