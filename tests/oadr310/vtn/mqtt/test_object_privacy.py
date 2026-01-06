"""
This module validates that the object privacy of events published to the MQTT broker is enforced.

In practice, this requires the following:

1. An event to be published in the VTN with a specific target, hereafter called target-A
2. A VEN object created within the VTN with target-A in the targets array (allowing the VEN to view objects with this target).
3. A subscription to a topic of /ven/{ven_id} with the ven_id being the ID of the object in step 2.
The subscriber in the MQTT broker MUST have the same client_id as the VEN object in step 2, otherwise topic subscription MUST be rejected.
4. Only events with the targets of the VEN object in step 2 (only target-A in this case) must be published to the MQTT topic of step 3.
"""

from urllib.parse import urlparse

import pytest
from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject
from tests.openadr310_vtn_test_container import OpenADR310VtnTestContainer
from paho.mqtt.enums import MQTTErrorCode

def test_mqtt_client_certificate_auth(
        integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer,
        certificate_mqtt_notifier_binding_object: MqttNotifierBindingObject) -> None:
    """Ensure the MQTT client can be created with certificate-based authentication."""
    mqtt_certificate_auth_url = urlparse(integration_test_openadr310_reference_vtn.get_mqtt_broker_certificate_url())
    client = MQTTClient(mqtt_notifier_binding=certificate_mqtt_notifier_binding_object)

    if mqtt_certificate_auth_url.hostname is None or mqtt_certificate_auth_url.port is None:
        pytest.fail("mqtt URL could not be parsed") 

    rc = client.connect(host=mqtt_certificate_auth_url.hostname, port=mqtt_certificate_auth_url.port)
    
    if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
        pytest.fail("Failed to connect to MQTT broker")