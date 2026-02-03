# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

import re
import threading
from collections import deque
from pathlib import Path
from types import TracebackType
from typing import Any, Self

import docker.errors
from testcontainers.core.container import DockerContainer, LogMessageWaitStrategy
from testcontainers.core.network import Network
from testcontainers.mqtt import MosquittoContainer

_LOG_BUFFER_MAX_LINES = 5_000


class OpenADR310RefImplementationVtnTestContainer:
    """A test container for an OpenADR 3.1.0 VTN."""

    def __init__(
        self,
        oauth_token_endpoint: str,
        oauth_jwks_url: str,
        network: Network | None = None,
        vtn_reference_image: str = "ghcr.io/nicburgt/oadr310-vtn-test:latest",
        vtn_port: int = 8080,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Initialize the VTN test container.

        Args:
            oauth_token_endpoint (str): The OAuth token endpoint URL for the VTN to use for token validation.
            oauth_jwks_url (str): The OAuth JWKS URL for the VTN to use for token validation.
            network (Network | None, optional): The Docker network to use. If None, a new network will be created.
            vtn_reference_image (str, optional): The Docker image reference for the VTN. Defaults to "ghcr.io/nicburgt/oadr310-vtn-test:latest".
            vtn_port (int, optional): The port on which the VTN will listen. Defaults to 8080.
            **kwargs: Additional arguments to pass to the DockerContainer constructor.

        """
        self._vtn_port = vtn_port
        self._log_stop_event = threading.Event()
        self._vtn_log_lines: deque[str] = deque(maxlen=_LOG_BUFFER_MAX_LINES)
        self._vtn_log_thread: threading.Thread | None = None

        # Configure the MQTT ports for the listeners which are configured in mosquitto.conf
        # This cannot be provided dynamically at runtime, since the mosquitto.conf must reflect the correct ports.
        self._mqtt_port_anonymous = 1883
        self._mqtt_port_certificate_auth = 8883

        if network is None:
            self._internal_network = True
            self._network = Network()
        else:
            self._internal_network = False
            self._network = network

        tests_root_dir = Path(__file__).resolve().parent

        self._mosquitto_config_file_dir = tests_root_dir / "mosquitto" / "mosquitto.conf"
        mosquitto_cert_dir = tests_root_dir / "mosquitto" / "certs"
        vtn_cert_dir = tests_root_dir / "certs" / "oadr310" / "vtn"

        # Initialize MQTT container, which is required by the VTN.
        self._mqtt = (
            MosquittoContainer(
                image="amd64/eclipse-mosquitto:2.0.22",
            )
            .with_kwargs(platform="linux/amd64")
            .with_volume_mapping(host=str(mosquitto_cert_dir), container="/mosquitto/certs", mode="ro")
            .with_network(self._network)
            .with_network_aliases("mqttbroker")
            .with_exposed_ports(self._mqtt_port_anonymous, self._mqtt_port_certificate_auth)
            .waiting_for(LogMessageWaitStrategy(re.compile(r"mosquitto version .* running")))
        )

        # Initialize VTN container with the static environment variables.
        self._vtn = (
            DockerContainer(vtn_reference_image, **kwargs)
            .with_kwargs(platform="linux/amd64")
            .with_network(self._network)
            .with_exposed_ports(self._vtn_port)
            # Use network alias to communicate with MQTT broker from VTN (same docker network).
            .with_env("MQTT_CLIENT_BROKER_HOST", "mqttbroker")
            .with_env("OIDC_AUTH_ENABLED", "True")
            .with_env("OIDC_TOKEN_URL", oauth_token_endpoint)
            .with_env("OIDC_JWKS_URL", oauth_jwks_url)
            .with_env("USE_TLS", "true")
            .with_env("TLS_CERT_FILE", "/vtn_certs/cert.pem")
            .with_env("TLS_KEY_FILE", "/vtn_certs/key.pem")
            .with_env("LOG_LEVEL", "10")  # Debug log level
            .with_volume_mapping(host=str(vtn_cert_dir), container="/vtn_certs", mode="ro")
            .waiting_for(LogMessageWaitStrategy(re.compile(r".*ListStore\.__init__\(\).*"), re.DOTALL))
        )

    def _start_vtn_log_capture(self) -> None:
        """Capture VTN logs into an in-memory ring buffer."""
        if self._vtn_log_thread is not None:
            return

        wrapped = self._vtn.get_wrapped_container()

        def _run() -> None:
            try:
                for chunk in wrapped.logs(stream=True, follow=True, stdout=True, stderr=True):
                    if self._log_stop_event.is_set():
                        break
                    chunk_bytes = chunk if isinstance(chunk, bytes | bytearray) else str(chunk).encode("utf-8", errors="replace")
                    text = chunk_bytes.decode("utf-8", errors="replace")
                    for line in text.splitlines():
                        if self._log_stop_event.is_set():
                            break
                        self._vtn_log_lines.append(line)
            except (docker.errors.DockerException, OSError):
                return

        self._vtn_log_thread = threading.Thread(target=_run, name="oadr310-ref-vtn-logs", daemon=True)
        self._vtn_log_thread.start()

    def get_vtn_log_tail(self, max_lines: int = 500) -> list[str]:
        """Return the last N captured VTN log lines (best-effort)."""
        if max_lines <= 0:
            return []
        if max_lines >= len(self._vtn_log_lines):
            return list(self._vtn_log_lines)
        return list(self._vtn_log_lines)[-max_lines:]

    def start(self) -> Self:
        """Start both containers and wait for them to be ready."""
        if self._internal_network:
            # Internal network, so we must create the network manually.
            self._network.create()

        self._mqtt.start(configfile=self._mosquitto_config_file_dir)

        # Configure the VTN with the MQTT broker URL prior to starting it.
        self._vtn.with_env("MQTT_VTN_BROKER_IP", "mqttbroker").with_env("MQTT_VTN_BROKER_PORT", self._mqtt.MQTT_PORT).with_env(
            "MQTT_CLIENT_BROKER_HOST", "mqttbroker"
        ).with_env("MQTT_CLIENT_BROKER_PORT", self._mqtt.MQTT_PORT).start()

        self._start_vtn_log_capture()
        return self

    def get_base_url(self) -> str:
        """Get the base URL for the VTN."""
        return f"https://localhost:{self._vtn.get_exposed_port(self._vtn_port)}/openadr3/3.1.0"

    def get_mqtt_broker_anonymous_url(self) -> str:
        """Get the MQTT broker URL for anonymous authentication."""
        return f"mqtt://localhost:{self._mqtt.get_exposed_port(self._mqtt_port_anonymous)}"

    def get_mqtt_broker_certificate_url(self) -> str:
        """Get the MQTT broker URL for certificate authentication."""
        return f"mqtts://localhost:{self._mqtt.get_exposed_port(self._mqtt_port_certificate_auth)}"

    def stop(self) -> None:
        """Stop the openleadr test container and its dependencies."""
        self._log_stop_event.set()
        self._vtn.stop()
        self._mqtt.stop()
        if self._internal_network:
            # Internal network, so we must remove the network ourselves.
            self._network.remove()

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.stop()
