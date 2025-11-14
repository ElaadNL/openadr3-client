import json
from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion
from openadr3_client._auth.token_manager import OAuthTokenManager
from openadr3_client.models.notifiers.mqtt.mqtt import MqttNotifierAuthenticationAnonymous, MqttNotifierAuthenticationCertificate, MqttNotifierAuthenticationOAuth2BearerToken, MqttNotifierBindingObject
from openadr3_client.logging import logger
from openadr3_client.models.notifiers.serialization import NotifierSerialization


class MQTTClient(Client):
    def __init__(self, mqtt_notifier_binding: MqttNotifierBindingObject, oauth_token_manager: OAuthTokenManager | None = None) -> None:
        """Initializes the MQTT client.

        Args:
            mqtt_notifier_binding (MqttNotifierBindingObject): MQTT notifier binding information.
        """
        super().__init__(callback_api_version=CallbackAPIVersion.VERSION2)
        self._mqtt_notifier_binding = mqtt_notifier_binding
        self._oauth_token_manager = oauth_token_manager

        self._enable_lifecycle_logging()
        self._configure_authentication()

    def _configure_authentication(self) -> None:
        """Configures the authentication of the MQTT client.

        Args:
            mqtt_notifier_binding (MqttNotifierBindingObject): MQTT notifier binding information.
        """
        if isinstance(self._mqtt_notifier_binding.authentication, MqttNotifierAuthenticationAnonymous):
            pass # No authentication needed.
        elif isinstance(self._mqtt_notifier_binding.authentication, MqttNotifierAuthenticationOAuth2BearerToken):
            if self._oauth_token_manager is None:
                raise ValueError("MQTTClient - oauth_token_manager is required when using oauth bearer authentication.")
            
            self.username_pw_set(password=self._oauth_token_manager.get_access_token())
            # Token refresh is handled with on_disconnect hook.
            self._configure_token_refresh_on_disconnect()
        elif isinstance(self._mqtt_notifier_binding.authentication, MqttNotifierAuthenticationCertificate):
            self.tls_set(
                ca_certs=self._mqtt_notifier_binding.authentication.ca_cert,
                certfile=self._mqtt_notifier_binding.authentication.client_cert,
                keyfile=self._mqtt_notifier_binding.authentication.client_key,
            )
            self.tls_insecure_set(value=False) # Require certificate verification.
    
    def _enable_lifecycle_logging(self) -> None:
        """Enable lifecycle logging for the MQTT client."""
        self.on_connect = lambda client, userdata, flags, rc, props: logger.info(
            f"Connected to broker with result code '{rc}'"
        )
        self.on_connect_fail = lambda client, userdata: logger.warning(
            "Failed to connect to broker"
        )
        self.on_publish = lambda client, userdata, mid, a, b: logger.debug(
            f"Published message with mid: {mid}. Reasoncode {a}"
        )
        self.on_disconnect = lambda client, userdata, flags, rc, props: logger.info(
            "Disconnected from MQTT broker"
        )
        self.on_subscribe = (
            lambda client, userdata, mid, granted_qos, properties: logger.debug(
                f"Subscribed to topic with mid: {mid} and QoS: {granted_qos}"
            )
        )
        self.on_unsubscribe = (
            lambda client, userdata, mid, granted_qos, properties: logger.debug(
                f"Unsubscribed from topic with mid: {mid} and QoS: {granted_qos}"
            )
        )

    def _configure_token_refresh_on_disconnect(self, client, userdata, flags, rc, props):
        # Capture any existing callback and call it as normal.
        existing_cb = self.on_disconnect

        def _on_disconnect_handler(client, userdata, flags, rc, props):
            if existing_cb is not None:
                existing_cb(client, userdata, flags, rc, props)

            # Handle token refresh callback only on unexpected disconnect.
            if rc != 0:
                self._refresh_token_on_disconnect()

        self.on_disconnect = _on_disconnect_handler

    def _refresh_token_on_disconnect(self) -> None:
        logger.debug("MQTTClient disconnected with non zero exit code, refreshing token and reconnecting.")
        self.username_pw_set(password=self._oauth_token_manager.get_access_token())
        try:
            self.reconnect()
        except Exception:
            logger.warning("MQTTClient - Failed to reconnect to MQTT broker with refreshed access token, aborting...")
            pass