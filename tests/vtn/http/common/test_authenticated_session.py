import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError

from openadr3_client._vtn.http.common._authenticated_session import _BearerAuthenticatedSession


@pytest.mark.usefixtures("integration_test_oauth_client")
def test_authenticated_session_contains_access_token() -> None:
    """Test to validate that an authenticated session automatically includes an access token in all requests."""
    session = _BearerAuthenticatedSession()

    header_before_request = session.headers.get("Authorization")

    with pytest.raises(RequestsConnectionError) as e:
        _ = session.get("http://localhost:51853")

    # Before the first call is made with the session, the header should be empty.
    assert header_before_request is None, "Authorization header should be empty before the first call."
    assert e.value.request is not None, "Request object should be provided in the exception."
    # No service is listening on localhost, but we can still access the original request object.
    authorization_header = e.value.request.headers.get("Authorization")
    assert isinstance(authorization_header, str), "Authorization header should be a string"
    assert authorization_header.startswith("Bearer "), "Authorization header should start with 'Bearer '"
    assert authorization_header.split("Bearer ")[1] is not None, "Value should be present after 'Bearer ' prefix."
