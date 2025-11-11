from abc import ABC
from enum import Enum
from typing import Literal, final
from pydantic import BaseModel, Field

from openadr3_client.models.notifiers.serialization import NotifierSerialization

@final
class MqttNotifierAuthenticationMethod(str, Enum):
    """Authentication methods supported by the MQTT notifiers."""

    ANONYMOUS = "ANONYMOUS"
    OAUTH2_BEARER_TOKEN = "OAUTH2_BEARER_TOKEN"
    CERTIFICATE = "CERTIFICATE"

class MqttNotifierAuthenticationBase(ABC, BaseModel):
    """Domain model representing the MQTT notifiers authentication mechanism."""

@final
class MqttNotifierAuthenticationAnonymous(MqttNotifierAuthenticationBase):
    """Represents anonymous authentication for the MQTT notifier."""

    method = Literal[MqttNotifierAuthenticationMethod.ANONYMOUS]
    """The authentication method."""

@final
class MqttNotifierAuthenticationOAuth2BearerToken(MqttNotifierAuthenticationBase):
    """Represents oauth2 bearer authentication for the MQTT notifier."""

    method = Literal[MqttNotifierAuthenticationMethod.OAUTH2_BEARER_TOKEN]
    """The authentication method."""

    username: str
    """Either the distinguished string "{clientID}", or any other literal string."""

@final
class MqttNotifierAuthenticationCertificate(MqttNotifierAuthenticationBase):
    """Represents certificate based authentication for the MQTT notifier."""

    method = Literal[MqttNotifierAuthenticationMethod.CERTIFICATE]
    """The authentication method."""

    ca_cert: str
    """String containing the Certificate Authority certificate."""

    client_cert: str
    """String containing the Client certificate."""

    client_key: str
    """String containing the client certificate private key."""

class MqttNotifierBindingObject(BaseModel):
    """Domain model representing an MQTT notifier binding.
    
    Contains Details of MQTT binding for messaging protocol support"""

    uris: list[str] = Field(alias="URIS")
    """URIs for connection to MQTT broker."""

    serialization: NotifierSerialization = Field(default=NotifierSerialization.JSON)
    """Serialization supported by the MQTT notifier."""

    authentication: MqttNotifierAuthenticationBase
    """Authentication method supported for connection to MQTT broker."""

class MqttTopicInformation(BaseModel):
    """Contains topic information of the MQTT notifier."""
    ...