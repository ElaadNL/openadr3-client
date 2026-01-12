from pathlib import Path
from urllib.parse import urlparse

import pytest
from pydantic import AnyUrl

from openadr3_client._auth.token_manager import OAuthTokenManager, OAuthTokenManagerConfig
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import (
    MqttNotifierAuthenticationAnonymous,
    MqttNotifierAuthenticationCertificate,
    MqttNotifierAuthenticationOAuth2BearerToken,
    MqttNotifierBindingObject,
)
from tests.conftest import IntegrationTestOAuthClient
from tests.openadr310_vtn_test_container import OpenADR310VtnTestContainer


@pytest.fixture(scope="session")
def oauth_token_manager_mqtt(integration_test_oauth_client: IntegrationTestOAuthClient) -> OAuthTokenManager:
    """
    Returns the OAUTH token manager for communicating with the oauth listener of the MQTT broker.

    Args:
        integration_test_oauth_client (IntegrationTestOAuthClient): The integration test oauth client to authenticate with.

    Returns:
        OAuthTokenManager: The configured oauth token manager

    """
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
def anonymous_mqtt_notifier_binding_object(integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer) -> MqttNotifierBindingObject:
    """
    A MQTT notifier binding object which is configured with anonymous authentication.

    Returns:
        MqttNotifierBindingObject: The configured MQTT notifier binding object.

    """
    mqtt_anonymous_auth_url = urlparse(integration_test_openadr310_reference_vtn.get_mqtt_broker_anonymous_url())
    return MqttNotifierBindingObject(URIS=[AnyUrl(mqtt_anonymous_auth_url.geturl())], authentication=MqttNotifierAuthenticationAnonymous())


@pytest.fixture(scope="session")
def oauth_mqtt_notifier_binding_object() -> MqttNotifierBindingObject:
    """
    A MQTT notifier binding object which is configured with OAUTH authentication.

    Returns:
        MqttNotifierBindingObject: The configured MQTT notifier binding object.

    """
    return MqttNotifierBindingObject(URIS=[AnyUrl("mqtt://localhost:1883")], authentication=MqttNotifierAuthenticationOAuth2BearerToken(username="test-client"))


@pytest.fixture(scope="session")
def certificate_mqtt_notifier_binding_object(integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer) -> MqttNotifierBindingObject:
    """
    A MQTT notifier binding object which is configured with certificate authentication.

    Returns:
        MqttNotifierBindingObject: The configured MQTT notifier binding object.

    """
    mqtt_certificate_auth_url = urlparse(integration_test_openadr310_reference_vtn.get_mqtt_broker_certificate_url())
    mosquitto_dir = Path(__file__).parent.parent.parent.parent / "mosquitto"

    return MqttNotifierBindingObject(
        URIS=[AnyUrl(mqtt_certificate_auth_url.geturl())],
        authentication=MqttNotifierAuthenticationCertificate(
            ca_cert=str(mosquitto_dir / "certs" / "ca.crt"),
            client_cert=str(mosquitto_dir / "certs" / "client.crt"),
            client_key=str(mosquitto_dir / "certs" / "client.key"),
        ),
    )
