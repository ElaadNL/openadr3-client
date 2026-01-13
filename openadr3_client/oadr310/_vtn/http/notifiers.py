# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""
Implements the communication with the notifiers interface of an OpenADR 3 VTN.

Notifiers was introduced in OpenADR 3.1, VTN implementations implementing earlier versions will not respond to this interface.
"""

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.logging import logger
from openadr3_client.oadr310._vtn.http.http_interface import AuthenticatedHttpInterface
from openadr3_client.oadr310._vtn.interfaces.notifiers import (
    ReadOnlyMqttNotifierInterface,
    ReadOnlyNotifierInterface,
)
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttTopicInformation
from openadr3_client.oadr310.models.notifiers.response import NotifierDetails

BASE_PREFIX = "notifiers"


class NotifiersReadOnlyHttpInterface(ReadOnlyNotifierInterface, ReadOnlyMqttNotifierInterface, AuthenticatedHttpInterface):
    """Implements the read communication with the notifiers HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, config=config, verify_tls_certificate=verify_tls_certificate)

    def _get_topic_information(self, request_name: str, url_appendix: str) -> MqttTopicInformation:
        """
        Retrieve topic information from the VTN.

        Args:
            request_name (str): The request name, used for logging purposes.
            url_appendix (str): The appendix to add to the vtn_base_url/base_prefix URL.
            This must not include the leading /.

        Returns:
            MqttTopicInformation: MQTT topic information retrieved from the VTN.

        """
        logger.debug(f"Notifiers - Performing {request_name} request")

        response = self.session.get(f"{self.base_url}/{BASE_PREFIX}/{url_appendix}")
        response.raise_for_status()

        return MqttTopicInformation.model_validate(response.json())

    def get_notifiers(self) -> NotifierDetails:
        logger.debug("Notifiers - Performing get_notifiers request")

        response = self.session.get(f"{self.base_url}/{BASE_PREFIX}")
        response.raise_for_status()

        return NotifierDetails.model_validate(response.json())

    def get_program_topics(self) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", "mqtt/topics/programs")

    def get_program_topics_for_id(self, program_id: str) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", f"mqtt/topics/programs/{program_id}")

    def get_event_topics(self) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", "mqtt/topics/events")

    def get_event_topics_for_program(self, program_id: str) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", f"mqtt/topics/programs/{program_id}/events")

    def get_report_topics(self) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", "mqtt/topics/reports")

    def get_subscription_topics(self) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", "mqtt/topics/subscriptions")

    def get_ven_topics(self) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", "mqtt/topics/vens")

    def get_ven_topics_for_id(self, ven_id: str) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", f"mqtt/topics/vens/{ven_id}")

    def get_resource_topics(self) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", "mqtt/topics/resources")

    def get_event_topics_for_ven(self, ven_id: str) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", f"mqtt/topics/vens/{ven_id}/events")

    def get_program_topics_for_ven(self, ven_id: str) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", f"mqtt/topics/vens/{ven_id}/programs")

    def get_resource_topics_for_ven(self, ven_id: str) -> MqttTopicInformation:
        return self._get_topic_information("get_program_topics", f"mqtt/topics/vens/{ven_id}/resources")
