try:
    from paho.mqtt.client import Client
    from paho.mqtt.enums import CallbackAPIVersion
except ImportError as e:
    msg = "Usage of the MQTT client requires the 'mqtt' extra. Install it with: pip install 'openadr3-client[mqtt]' or the equivalent in your package manager."
    raise ImportError(msg) from e

from openadr3_client._auth.token_manager import OAuthTokenManager
from openadr3_client.logging import logger
from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import (
    MqttNotifierAuthenticationAnonymous,
    MqttNotifierAuthenticationCertificate,
    MqttNotifierAuthenticationOAuth2BearerToken,
    MqttNotifierBindingObject,
)


class MQTTClient(Client):
    def __init__(self, mqtt_notifier_binding: MqttNotifierBindingObject, oauth_token_manager: OAuthTokenManager | None = None) -> None:
        """
        Initializes the MQTT client.

        Args:
            mqtt_notifier_binding (MqttNotifierBindingObject): MQTT notifier binding information.
            oauth_token_manager (OAuthTokenManager | None): The oauth token manager of the MQTT client, defaults to None.

        """
        super().__init__(callback_api_version=CallbackAPIVersion.VERSION2)
        self._mqtt_notifier_binding = mqtt_notifier_binding
        self._oauth_token_manager = oauth_token_manager

        self._enable_lifecycle_logging()
        self._configure_authentication()

    def _configure_authentication(self) -> None:
        """
        Configures the authentication of the MQTT client.

        Args:
            mqtt_notifier_binding (MqttNotifierBindingObject): MQTT notifier binding information.

        """
        if isinstance(self._mqtt_notifier_binding.authentication, MqttNotifierAuthenticationAnonymous):
            pass  # No authentication needed.
        elif isinstance(self._mqtt_notifier_binding.authentication, MqttNotifierAuthenticationOAuth2BearerToken):
            if self._oauth_token_manager is None:
                err_msg = "MQTTClient - oauth_token_manager is required when using oauth bearer authentication."
                raise ValueError(err_msg)

            self.username_pw_set(username=None, password=self._oauth_token_manager.get_access_token())
            # Token refresh is handled with on_disconnect hook.
            self._configure_token_refresh_on_disconnect()
        elif isinstance(self._mqtt_notifier_binding.authentication, MqttNotifierAuthenticationCertificate):
            self.tls_set(
                ca_certs=self._mqtt_notifier_binding.authentication.ca_cert,
                certfile=self._mqtt_notifier_binding.authentication.client_cert,
                keyfile=self._mqtt_notifier_binding.authentication.client_key,
            )
            self.tls_insecure_set(value=False)  # Require certificate verification.

    def _enable_lifecycle_logging(self) -> None:
        """Enable lifecycle logging for the MQTT client."""
        self.on_connect = lambda _client, _userdata, _flags, rc, _props: logger.info(f"Connected to broker with result code '{rc}'")
        self.on_connect_fail = lambda _client, _userdata: logger.warning("Failed to connect to broker")
        self.on_publish = lambda _client, _userdata, mid, a, _b: logger.debug(f"Published message with mid: {mid}. Reasoncode {a}")
        self.on_disconnect = lambda client, userdata, rc, properties=None: logger.info("Disconnected from MQTT broker")  # noqa: ARG005
        self.on_subscribe = lambda _client, _userdata, mid, granted_qos, _properties: logger.debug(f"Subscribed to topic with mid: {mid} and QoS: {granted_qos}")
        self.on_unsubscribe = lambda _client, _userdata, mid, granted_qos, _properties: logger.debug(f"Unsubscribed from topic with mid: {mid} and QoS: {granted_qos}")

    def _configure_token_refresh_on_disconnect(self) -> None:
        # Capture any existing callback and call it as normal.
        existing_cb = self.on_disconnect

        def _on_disconnect_handler(*args, **kwargs):  # noqa: ANN202
            # handle signature differences from mqtt to fetch rc (reason-code) in a safe manner.
            mqtt_v3_args_count = 3
            mqtt_v5_minimum_args_count = 4

            if len(args) == mqtt_v3_args_count:
                # MQTT v3
                rc = args[2]
            elif len(args) >= mqtt_v5_minimum_args_count:
                # MQTT v5
                rc = args[3]
            else:
                rc = None  # defensive fallback

            if existing_cb is not None:
                existing_cb(*args, **kwargs)

            # Handle token refresh callback only on unexpected disconnect.
            if rc is not None and rc != 0:
                self._refresh_token_on_disconnect()

        self.on_disconnect = _on_disconnect_handler

    def _refresh_token_on_disconnect(self) -> None:
        logger.debug("MQTTClient disconnected with non zero exit code, refreshing token and reconnecting.")
        if self._oauth_token_manager is None:
            err_msg = "MQTTClient - oauth_token_manager is required to refresh access token on disconnect."
            raise ValueError(err_msg)
        self.username_pw_set(username=None, password=self._oauth_token_manager.get_access_token())
        try:
            self.reconnect()
        except Exception:  # noqa: BLE001
            logger.warning("MQTTClient - Failed to reconnect to MQTT broker with refreshed access token, aborting...")
