# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field

from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttNotifierBindingObject


class NotifierDetails(BaseModel):
    """Domain model representing the details on configured notifiers of the VTN."""

    webhook: bool = Field(alias="WEBHOOK")
    mqtt: MqttNotifierBindingObject = Field(alias="MQTT")
