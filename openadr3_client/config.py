"""Contains configuration variables used by the OpenADR3 client."""

from decouple import config

# AUTH MODULE

OAUTH_TOKEN_ENDPOINT = config("OAUTH_TOKEN_ENDPOINT")
OAUTH_CLIENT_ID = config('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = config('OAUTH_CLIENT_SECRET')

