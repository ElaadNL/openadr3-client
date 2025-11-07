"""Implements the abstract base classes for VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client.models.auth.auth_server import AuthServerInfo


class ReadOnlyAuthInterface(ABC):
    """Abstract class which contains the interface for read only methods of the VTN auth module."""

    @abstractmethod
    def get_auth_server(self) -> AuthServerInfo:
        """
        Discover information related to the authorization service used by the VTN.

        Returns:
            AuthServerInfo: Information related to the authorization service used by the VTN.
        """