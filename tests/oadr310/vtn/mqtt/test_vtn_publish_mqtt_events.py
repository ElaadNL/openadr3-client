"""This module validates that the VTN publishes messages to the MQTT broker when changes are made in the VTN."""

import json
import threading
from urllib.parse import urlparse

import pytest
from paho.mqtt.enums import MQTTErrorCode

from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import event_in_program_with_targets, new_program, ven_with_targets
from tests.openadr310_vtn_test_container import OpenADR310VtnTestContainer


def test_retrieve_mqtt_message_when_changes_are_made_in_vtn(
    integration_test_openadr310_reference_vtn: OpenADR310VtnTestContainer,
    vtn_openadr_310_bl_token: IntegrationTestVTNClient,
    certificate_mqtt_notifier_binding_object: MqttNotifierBindingObject,
) -> None:
    """Verifies that MQTT messages are published by the VTN when changes occur in the VTN."""
    mqtt_certificate_auth_url = urlparse(integration_test_openadr310_reference_vtn.get_mqtt_broker_certificate_url())
    client = MQTTClient(mqtt_notifier_binding=certificate_mqtt_notifier_binding_object)

    if mqtt_certificate_auth_url.hostname is None or mqtt_certificate_auth_url.port is None:
        pytest.fail("mqtt URL could not be parsed")

    rc = client.connect(host=mqtt_certificate_auth_url.hostname, port=mqtt_certificate_auth_url.port)

    if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
        pytest.fail("Failed to connect to MQTT broker")

    received_messages = []
    message_received = threading.Event()

    def on_message(_client, _userdata, msg):  # noqa: ANN001, ANN202
        received_messages.append(msg)
        message_received.set()

    client.on_message = on_message

    client.loop_start()

    try:
        with (
            ven_with_targets(vtn_openadr_310_bl_token, ven_name="my-ven", client_id_of_ven="client-id", targets=("test-target",)) as my_ven,
            new_program(vtn_openadr_310_bl_token, program_name="test-program-mqtt-receive-fail") as created_program,
            event_in_program_with_targets(
                vtn_openadr_310_bl_token, program=created_program, intervals=(), event_name="test-event-mqtt-requuest-fail", targets=("test-target",)
            ) as my_event,
        ):
            client.subscribe("#")  # Subscribe to all topics to capture all events published.
            message_received.wait(timeout=5.0)  # Wait for 5 seconds.
    finally:
        client.loop_stop()
        client.disconnect()

    # Validate that MQTT messages are received
    assert len(received_messages) > 0

    # Extract the payload from the messages, this contains the actual event.
    payloads = [json.loads(message.payload) for message in received_messages]

    create_mqtt_messages = [p for p in payloads if p["operation"] == "CREATE"]
    delete_mqtt_messages = [p for p in payloads if p["operation"] == "DELETE"]

    # Verify that no other messages were published (e.g. UPDATE)
    assert len(payloads) == (len(create_mqtt_messages) + len(delete_mqtt_messages))

    # Validate that for each object
    # Exactly one CREATE and exactly one DELETE MQTT message is received. (DELETE since the
    # context manager will delete the object after it exits).
    created_event_mqtt_message = next((x for x in create_mqtt_messages if x["object_type"] == "EVENT" and x["object"]["id"] == my_event.id), None)
    created_program_mqtt_message = next((x for x in create_mqtt_messages if x["object_type"] == "PROGRAM" and x["object"]["id"] == created_program.id), None)
    created_ven_mqtt_message = next((x for x in create_mqtt_messages if x["object_type"] == "VEN" and x["object"]["id"] == my_ven.id), None)

    deleted_event_mqtt_message = next((x for x in delete_mqtt_messages if x["object_type"] == "EVENT" and x["object"]["id"] == my_event.id), None)
    deleted_program_mqtt_message = next((x for x in delete_mqtt_messages if x["object_type"] == "PROGRAM" and x["object"]["id"] == created_program.id), None)
    deleted_ven_mqtt_message = next((x for x in delete_mqtt_messages if x["object_type"] == "VEN" and x["object"]["id"] == my_ven.id), None)

    assert created_event_mqtt_message is not None
    assert created_program_mqtt_message is not None
    assert created_ven_mqtt_message is not None
    assert deleted_event_mqtt_message is not None
    assert deleted_program_mqtt_message is not None
    assert deleted_ven_mqtt_message is not None
