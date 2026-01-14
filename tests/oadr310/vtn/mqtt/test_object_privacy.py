# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""
This module validates that the object privacy of events published to the MQTT broker is enforced.

In practice, this requires the following:

1. An event to be published in the VTN with a specific target, hereafter called target-A
2. A VEN object created within the VTN with target-A in the targets array (allowing the VEN to view objects with this target).
3. A subscription to a topic of /ven/{ven_id} with the ven_id being the ID of the object in step 2.
The subscriber in the MQTT broker MUST have the same client_id as the VEN object in step 2, otherwise topic subscription MUST be rejected.
4. Only events with the targets of the VEN object in step 2 (only target-A in this case) must be published to the MQTT topic of step 3.

Note that these tests are not currently implemented, because the OpenADR 3.1 reference implementation does not yet implement object privacy
in the MQTT broker: https://github.com/oadr3-org/openadr3-vtn-reference-implementation/pull/174. For this reason, the corrosponding
test is skipped for now.
"""

import threading

import pytest

from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject
from tests.conftest import IntegrationTestVTNClient
from tests.oadr310.generators import event_in_program_with_targets, new_program, ven_with_targets
from tests.oadr310.vtn.mqtt.generators import with_mqtt_client


@pytest.mark.skip(reason="Object privacy on MQTT broker not yet implemented in OpenADR 3.1 reference vtn...")
def test_dont_receive_mqtt_message_not_assigned_to_ven(
    vtn_openadr_310_bl_token: IntegrationTestVTNClient,
    certificate_mqtt_notifier_binding_object: MqttNotifierBindingObject,
) -> None:
    """Verifies that an MQTT message not assigned to a VEN cannot be read by subscribing to that VENs personal topic in the MQTT broker."""
    received_messages = []
    message_received = threading.Event()

    def on_message(_client, _userdata, msg):  # noqa: ANN001, ANN202
        received_messages.append(msg)
        message_received.set()

    with (
        ven_with_targets(vtn_openadr_310_bl_token, ven_name="my-ven", client_id_of_ven="client-id", targets=()) as my_ven,
        new_program(vtn_openadr_310_bl_token, program_name="test-program-mqtt-receive-fail") as created_program,
        event_in_program_with_targets(vtn_openadr_310_bl_token, program=created_program, intervals=(), event_name="test-event-mqtt-requuest-fail", targets=("test-target",)),
        with_mqtt_client(notifier_binding=certificate_mqtt_notifier_binding_object, on_message=on_message) as mqtt_client,
    ):
        mqtt_client.subscribe(f"/ven/{my_ven.id}")

        message_received.wait(timeout=5.0)  # Wait for 5 seconds.

    assert len(received_messages) == 0


@pytest.mark.skip(reason="Object privacy on MQTT broker not yet implemented in OpenADR 3.1 reference vtn...")
def test_retrieve_mqtt_message_assigned_to_ven(
    vtn_openadr_310_bl_token: IntegrationTestVTNClient,
    certificate_mqtt_notifier_binding_object: MqttNotifierBindingObject,
) -> None:
    """Verifies that an MQTT message assigned to a VEN can be read by subscribing to that VENs personal topic in the MQTT broker."""
    received_messages = []
    message_received = threading.Event()

    def on_message(_client, _userdata, msg):  # noqa: ANN001, ANN202
        received_messages.append(msg)
        message_received.set()

    with (
        ven_with_targets(vtn_openadr_310_bl_token, ven_name="my-ven", client_id_of_ven="client-id", targets=("test-target",)) as my_ven,
        new_program(vtn_openadr_310_bl_token, program_name="test-program-mqtt-receive-fail") as created_program,
        event_in_program_with_targets(vtn_openadr_310_bl_token, program=created_program, intervals=(), event_name="test-event-mqtt-requuest-fail", targets=("test-target",)),
        with_mqtt_client(notifier_binding=certificate_mqtt_notifier_binding_object, on_message=on_message) as mqtt_client,
    ):
        mqtt_client.subscribe(f"/ven/{my_ven.id}")

        message_received.wait(timeout=5.0)  # Wait for 5 seconds.

    assert len(received_messages) > 0
