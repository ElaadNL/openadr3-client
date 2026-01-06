
from pathlib import Path

import pytest

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierAuthenticationAnonymous, MqttNotifierBindingObject, MqttNotifierAuthenticationOAuth2BearerToken, MqttNotifierAuthenticationCertificate
from tests.conftest import IntegrationTestOAuthClient

@pytest.fixture(scope="session")
def oauth_token_manager_mqtt(integration_test_oauth_client: IntegrationTestOAuthClient) -> OAuthTokenManager:
   return OAuthTokenManager(
        config=OAuthTokenManagerConfig(
            client_id=integration_test_oauth_client.client_id,
            client_secret=integration_test_oauth_client.client_secret,
            token_url=integration_test_oauth_client.token_url,
            scopes=None,
            audience=None,
        )
    )

@pytest.fixture(scope="session")
def anonymous_mqtt_notifier_binding_object() -> MqttNotifierBindingObject:
    """A MQTT notifier binding object which is configured with anonymous authentication.

    Returns:
        MqttNotifierBindingObject: The configured MQTT notifier binding object.
    """
    return MqttNotifierBindingObject(
        URIS=["test"],
        authentication=MqttNotifierAuthenticationAnonymous()
    )

@pytest.fixture(scope="session")
def oauth_mqtt_notifier_binding_object() -> MqttNotifierBindingObject:
    """A MQTT notifier binding object which is configured with OAUTH authentication.

    Returns:
        MqttNotifierBindingObject: The configured MQTT notifier binding object.
    """
    return MqttNotifierBindingObject(
        URIS=["test"],
        authentication=MqttNotifierAuthenticationOAuth2BearerToken(username="test-client")
    )

@pytest.fixture(scope="session")
def certificate_mqtt_notifier_binding_object() -> MqttNotifierBindingObject:
    """A MQTT notifier binding object which is configured with certificate authentication.

    Returns:
        MqttNotifierBindingObject: The configured MQTT notifier binding object.
    """
    return MqttNotifierBindingObject(
        URIS=["test"],
        authentication=MqttNotifierAuthenticationCertificate(
            ca_cert=str(Path(__file__).parent.parent.parent.parent / "mosquitto" / "certs" / "ca.crt"),
            client_cert=str(Path(__file__).parent.parent.parent.parent / "mosquitto" / "certs" / "client.crt"),
            client_key=str(Path(__file__).parent.parent.parent.parent / "mosquitto" / "certs" / "client.key"),
        )
    )