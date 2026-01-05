"""This module validates that all the defined authentication mechanisms work for connecting to the MQTT broker."""

from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient


def test_mqtt_client_anonymous_auth(anonymous_mqtt_notifier_binding) -> None:
    """Ensure the MQTT client can be created with anonymous authentication."""
    client = MQTTClient(mqtt_notifier_binding=anonymous_mqtt_notifier_binding)

    assert isinstance(client, MQTTClient)


def test_mqtt_client_oauth2_bearer_auth(
    oauth2_mqtt_notifier_binding,
    oauth_token_manager,
) -> None:
    """Ensure the MQTT client can be created with OAuth2 bearer token authentication."""
    client = MQTTClient(
        mqtt_notifier_binding=oauth2_mqtt_notifier_binding,
        oauth_token_manager=oauth_token_manager,
    )

    assert isinstance(client, MQTTClient)


def test_mqtt_client_certificate_auth(certificate_mqtt_notifier_binding) -> None:
    """Ensure the MQTT client can be created with certificate-based authentication."""
    client = MQTTClient(mqtt_notifier_binding=certificate_mqtt_notifier_binding)

    assert isinstance(client, MQTTClient)
