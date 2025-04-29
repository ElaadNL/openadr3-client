from openadr3_client._vtn.http.common._authenticated_session import _BearerAuthenticatedSession
from requests.exceptions import ConnectionError as RequestsConnectionError
from tests.conftest import IntegrationTestOAuthClient


def test_authenticated_session_contains_access_token(integration_test_oauth_client: IntegrationTestOAuthClient) -> None:
    """Test to validate that an authenticated session automatically includes an access token in all requests."""
    session = _BearerAuthenticatedSession()

    # Before the first call is made with the session, the header should be empty.
    assert session.headers.get("Authorization") is None, "Authorization header should be empty before the first call."

    try:
        response = session.get("http://localhost:51853")
    except RequestsConnectionError as e:
        assert e.request is not None, "Request object should be provided in the exception."
        # No service is listening on localhost, but we can still access the original request object.
        authorization_header = e.request.headers.get("Authorization")
        assert isinstance(authorization_header, str), "Authorization header should be a string"
        assert authorization_header.startswith("Bearer "), "Authorization header should start with 'Bearer '"
        assert authorization_header.split("Bearer ")[1] is not None, "Value should be present after 'Bearer ' prefix."