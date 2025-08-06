from typing import final

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client._vtn.http.events import EventsHttpInterface
from openadr3_client._vtn.http.programs import ProgramsHttpInterface
from openadr3_client._vtn.http.reports import ReportsReadOnlyHttpInterface
from openadr3_client._vtn.http.subscriptions import SubscriptionsReadOnlyHttpInterface
from openadr3_client._vtn.http.vens import VensHttpInterface
from openadr3_client.bl._client import BusinessLogicClient


@final
class BusinessLogicHttpClientFactory:
    """Factory which can be used to create a business logic http client."""

    @staticmethod
    def create_http_bl_client(
        vtn_base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        scopes: list[str] | None = None,
        audience: str | None = None,
    ) -> BusinessLogicClient:
        """
        Creates a business logic client which uses the HTTP interface of a VTN.

        Args:
            vtn_base_url (str): The base URL for the HTTP interface of the VTN.
            client_id (str): The client id to use to provision an access token from the OAuth authorization server.
            client_secret (str): The client secret to use to provision an access token from the OAuth authorization server.
            token_url (str): The endpoint to provision access tokens from.
            scopes (list[str]): The scopes to request with the token. If empty, no scopes are requested.
            audience (str): The audience to request with the token. If empty, no audience is requested.

        """  # noqa: E501
        config = OAuthTokenManagerConfig(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scopes=scopes,
            audience=audience,
        )

        return BusinessLogicClient(
            events=EventsHttpInterface(
                base_url=vtn_base_url,
                config=config,
            ),
            programs=ProgramsHttpInterface(
                base_url=vtn_base_url,
                config=config,
            ),
            reports=ReportsReadOnlyHttpInterface(
                base_url=vtn_base_url,
                config=config,
            ),
            vens=VensHttpInterface(
                base_url=vtn_base_url,
                config=config,
            ),
            subscriptions=SubscriptionsReadOnlyHttpInterface(
                base_url=vtn_base_url,
                config=config,
            ),
        )
