# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Generator
from contextlib import contextmanager
from typing import final

from paho.mqtt.client import CallbackOnMessage
from paho.mqtt.enums import MQTTErrorCode

from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject


@final
class MQTTConnectionError(Exception):
    """Raised when the MQTT client fails to connect to the MQTT broker."""


@contextmanager
def with_mqtt_client(notifier_binding: MqttNotifierBindingObject, on_message: CallbackOnMessage) -> Generator[MQTTClient, None, None]:
    """
    Creates and configures an MQTT client which is connected using the notifier binding.

    Args:
        notifier_binding: The MQTT notifier binding configuration to connect with.
        on_message: The callback function to handle incoming messages.

    Yields:
        An instance of MQTTClient connected to the broker.

    """
    client = MQTTClient(mqtt_notifier_binding=notifier_binding)

    mqtt_url = notifier_binding.uris[0]

    if mqtt_url.host is None or mqtt_url.port is None:
        exc_msg = "MQTT broker URI is missing host or port"
        raise MQTTConnectionError(exc_msg)

    rc = client.connect(host=mqtt_url.host, port=mqtt_url.port)

    if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
        exc_msg = "Failed to connect to MQTT broker"
        raise MQTTConnectionError(exc_msg)

    client.loop_start()
    client.on_message = on_message

    try:
        yield client
    finally:
        client.loop_stop()
        client.disconnect()
