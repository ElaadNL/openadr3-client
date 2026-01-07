"""This module validates that all the defined authentication mechanisms work for connecting to the MQTT broker."""

from urllib.parse import urlparse

import pytest
from paho.mqtt.enums import MQTTErrorCode

from openadr3_client._auth.token_manager import OAuthTokenManager
from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject
from tests.openadr310_vtn_test_container import OpenADR310VtnTestContainer


def test_mqtt_client_anonymous_auth(
    integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer, anonymous_mqtt_notifier_binding_object: MqttNotifierBindingObject
) -> None:
    """Ensure the MQTT client can be created and connect with anonymous authentication."""
    mqtt_anonymous_url = urlparse(integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url())
    client = MQTTClient(mqtt_notifier_binding=anonymous_mqtt_notifier_binding_object)

    if mqtt_anonymous_url.hostname is None or mqtt_anonymous_url.port is None:
        pytest.fail("mqtt URL could not be parsed")

    rc = client.connect(host=mqtt_anonymous_url.hostname, port=mqtt_anonymous_url.port)

    if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
        pytest.fail("Failed to connect to MQTT broker")


def test_mqtt_client_oauth2_bearer_auth(
    oauth_mqtt_notifier_binding_object: MqttNotifierBindingObject,
    oauth_token_manager_mqtt: OAuthTokenManager,
) -> None:
    """Ensure the MQTT client can be created with OAuth2 bearer token authentication."""
    client = MQTTClient(
        mqtt_notifier_binding=oauth_mqtt_notifier_binding_object,
        oauth_token_manager=oauth_token_manager_mqtt,
    )

    assert isinstance(client, MQTTClient)


def test_mqtt_client_certificate_auth(
    integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer, certificate_mqtt_notifier_binding_object: MqttNotifierBindingObject
) -> None:
    """Ensure the MQTT client can be created and connect with certificate-based authentication."""
    mqtt_certificate_auth_url = urlparse(integration_test_openadr310_reference_vtn.get_mqtt_broker_certificate_url())
    client = MQTTClient(mqtt_notifier_binding=certificate_mqtt_notifier_binding_object)

    if mqtt_certificate_auth_url.hostname is None or mqtt_certificate_auth_url.port is None:
        pytest.fail("mqtt URL could not be parsed")

    rc = client.connect(host=mqtt_certificate_auth_url.hostname, port=mqtt_certificate_auth_url.port)

    if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
        pytest.fail("Failed to connect to MQTT broker")
