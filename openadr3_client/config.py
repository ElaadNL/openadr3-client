"""Contains configuration variables used by the OpenADR3 client."""

from decouple import config

# AUTH MODULE
OAUTH_TOKEN_ENDPOINT = config("OAUTH_TOKEN_ENDPOINT")
"""The endpoint to provision access tokens from."""
OAUTH_CLIENT_ID = config("OAUTH_CLIENT_ID")
"""The client id to use to provision an access token from the OAuth authorization server."""
OAUTH_CLIENT_SECRET = config("OAUTH_CLIENT_SECRET")
"""The client secret to use to provision an access token from the OAuth authorization server."""
_OAUTH_SCOPES = config("OAUTH_SCOPES", default="")
"""Comma delimited list of OAUTH scopes to request with the token, an empty string is interpreted as None."""
OAUTH_SCOPES = _OAUTH_SCOPES.split(",") if _OAUTH_SCOPES != "" else None
