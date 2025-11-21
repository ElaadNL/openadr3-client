from pydantic import BaseModel, Field

from openadr3_client.models.oadr310.notifiers.mqtt.mqtt import MqttNotifierBindingObject


class NotifierDetails(BaseModel):
    """Domain model representing the details on configured notifiers of the VTN."""

    webhook: bool = Field(alias="WEBHOOK")
    mqtt: MqttNotifierBindingObject = Field(alias="MQTT")
