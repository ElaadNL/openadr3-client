# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC
from enum import StrEnum
from typing import Literal, final

from pydantic import AnyUrl, BaseModel, Field

from openadr3_client.oadr310.models.notifiers.serialization import NotifierSerialization


@final
class MqttNotifierAuthenticationMethod(StrEnum):
    """Authentication methods supported by the MQTT notifiers."""

    ANONYMOUS = "ANONYMOUS"
    OAUTH2_BEARER_TOKEN = "OAUTH2_BEARER_TOKEN"  # noqa: S105 # nosec (False positive by bandit for oauth token)
    CERTIFICATE = "CERTIFICATE"


class MqttNotifierAuthenticationBase(ABC, BaseModel):
    """Domain model representing the MQTT notifiers authentication mechanism."""


@final
class MqttNotifierAuthenticationAnonymous(MqttNotifierAuthenticationBase):
    """Represents anonymous authentication for the MQTT notifier."""

    method: Literal[MqttNotifierAuthenticationMethod.ANONYMOUS] = MqttNotifierAuthenticationMethod.ANONYMOUS
    """The authentication method."""


@final
class MqttNotifierAuthenticationOAuth2BearerToken(MqttNotifierAuthenticationBase):
    """Represents oauth2 bearer authentication for the MQTT notifier."""

    method: Literal[MqttNotifierAuthenticationMethod.OAUTH2_BEARER_TOKEN] = MqttNotifierAuthenticationMethod.OAUTH2_BEARER_TOKEN
    """The authentication method."""

    username: str
    """Either the distinguished string "{clientID}", or any other literal string."""


@final
class MqttNotifierAuthenticationCertificate(MqttNotifierAuthenticationBase):
    """Represents certificate based authentication for the MQTT notifier."""

    method: Literal[MqttNotifierAuthenticationMethod.CERTIFICATE] = MqttNotifierAuthenticationMethod.CERTIFICATE
    """The authentication method."""

    ca_cert: str
    """String containing the Certificate Authority certificate."""

    client_cert: str
    """String containing the Client certificate."""

    client_key: str
    """String containing the client certificate private key."""


class MqttNotifierBindingObject(BaseModel):
    """
    Domain model representing an MQTT notifier binding.

    Contains Details of MQTT binding for messaging protocol support
    """

    uris: list[AnyUrl] = Field(alias="URIS")
    """URIs for connection to MQTT broker."""

    serialization: NotifierSerialization = Field(default=NotifierSerialization.JSON)
    """Serialization supported by the MQTT notifier."""

    authentication: MqttNotifierAuthenticationBase
    """Authentication method supported for connection to MQTT broker."""


class MqttNotifierTopicOperations(BaseModel):
    """Contains topic operations of a topic in the MQTT notifier."""

    create: str = Field(alias="CREATE")
    """'Topic path for CREATE operations."""

    update: str = Field(alias="UPDATE")
    """'Topic path for UPDATE operations."""

    delete: str = Field(alias="DELETE")
    """'Topic path for DELETE operations."""

    all: str = Field(alias="ALL")
    """'Topic path for ALL operations."""


class MqttTopicInformation(BaseModel):
    """Contains topic information of the MQTT notifier."""

    topics: MqttNotifierTopicOperations
    """Topic operations available as part of the MQTT notifier."""
