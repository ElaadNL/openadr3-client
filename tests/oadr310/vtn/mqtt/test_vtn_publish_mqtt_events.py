"""This module validates that the VTN publishes messages to the MQTT broker when changes are made in the VTN."""

import json
import time

from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import event_in_program_with_targets, new_program, ven_with_targets
from tests.oadr310.vtn.mqtt.generators import with_mqtt_client


def test_retrieve_mqtt_message_when_changes_are_made_in_vtn(
    vtn_openadr_310_bl_token: IntegrationTestVTNClient,
    certificate_mqtt_notifier_binding_object: MqttNotifierBindingObject,
) -> None:
    """Verifies that MQTT messages are published by the VTN when changes occur in the VTN."""
    received_messages = []

    def on_message(_client, _userdata, msg):  # noqa: ANN001, ANN202
        received_messages.append(msg)

    with (
        ven_with_targets(vtn_openadr_310_bl_token, ven_name="my-ven", client_id_of_ven="client-id", targets=("test-target",)) as my_ven,
        new_program(vtn_openadr_310_bl_token, program_name="test-program-mqtt-receive-fail") as created_program,
        event_in_program_with_targets(
            vtn_openadr_310_bl_token, program=created_program, intervals=(), event_name="test-event-mqtt-requuest-fail", targets=("test-target",)
        ) as my_event,
        with_mqtt_client(notifier_binding=certificate_mqtt_notifier_binding_object, on_message=on_message) as mqtt_client,
    ):
        mqtt_client.subscribe("#")  # Subscribe to all topics to capture all events published.
        time.sleep(5)  # Allow some time for messages to be processed.

    # Validate that MQTT messages are received
    assert len(received_messages) > 0

    # Extract the payload from the messages, this contains the actual event.
    payloads = [json.loads(message.payload) for message in received_messages]
    create_mqtt_messages = [p for p in payloads if p["operation"] == "CREATE"]

    # Validate that for each object exactly one CREATE MQTT message is received.
    created_event_mqtt_message = any(x for x in create_mqtt_messages if x["object_type"] == "EVENT" and x["object"]["id"] == my_event.id)
    created_program_mqtt_message = any(x for x in create_mqtt_messages if x["object_type"] == "PROGRAM" and x["object"]["id"] == created_program.id)
    created_ven_mqtt_message = any(x for x in create_mqtt_messages if x["object_type"] == "VEN" and x["object"]["id"] == my_ven.id)

    assert created_event_mqtt_message is True
    assert created_program_mqtt_message is True
    assert created_ven_mqtt_message is True
