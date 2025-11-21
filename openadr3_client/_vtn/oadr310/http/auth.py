"""Implements the communication with the auth interface of an OpenADR 3 VTN."""

from openadr3_client._vtn.oadr310.http.http_interface import AnonymousHttpInterface
from openadr3_client._vtn.oadr310.interfaces.auth import ReadOnlyAuthInterface
from openadr3_client.logging import logger
from openadr3_client.models.oadr310.auth.auth_server import AuthServerInfo

base_prefix = "auth"


class AuthReadOnlyInterface(ReadOnlyAuthInterface, AnonymousHttpInterface):
    """Implements the read communication with the auth HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, verify_tls_certificate=verify_tls_certificate)

    def get_auth_server(self) -> AuthServerInfo:
        """
        Discover information related to the authorization service used by the VTN.

        Returns:
            AuthServerInfo: Information related to the authorization service used by the VTN.

        """
        logger.debug("Auth - Performing get_auth_server request")

        response = self.session.get(f"{self.base_url}/{base_prefix}/server")
        response.raise_for_status()

        return AuthServerInfo.model_validate(response.json())
