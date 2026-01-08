"""This module validates that all the defined authentication mechanisms work for connecting to the MQTT broker."""

import pytest
from paho.mqtt.enums import MQTTErrorCode

from openadr3_client._auth.token_manager import OAuthTokenManager
from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject


def test_mqtt_client_anonymous_auth(anonymous_mqtt_notifier_binding_object: MqttNotifierBindingObject) -> None:
    """Ensure the MQTT client can be created and connect with anonymous authentication."""
    client = MQTTClient(mqtt_notifier_binding=anonymous_mqtt_notifier_binding_object)

    mqtt_anonymous_uri = anonymous_mqtt_notifier_binding_object.uris[0]

    if mqtt_anonymous_uri.host is None or mqtt_anonymous_uri.port is None:
        pytest.fail("MQTT broker URI is missing host or port for anonymous authentication test")

    rc = client.connect(host=mqtt_anonymous_uri.host, port=mqtt_anonymous_uri.port)

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


def test_mqtt_client_certificate_auth(certificate_mqtt_notifier_binding_object: MqttNotifierBindingObject) -> None:
    """Ensure the MQTT client can be created and connect with certificate-based authentication."""
    client = MQTTClient(mqtt_notifier_binding=certificate_mqtt_notifier_binding_object)

    mqtt_certificate_auth_url = certificate_mqtt_notifier_binding_object.uris[0]

    if mqtt_certificate_auth_url.host is None or mqtt_certificate_auth_url.port is None:
        pytest.fail("MQTT broker URI is missing host or port for certificate authentication test")

    rc = client.connect(host=mqtt_certificate_auth_url.host, port=mqtt_certificate_auth_url.port)

    if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
        pytest.fail("Failed to connect to MQTT broker")
