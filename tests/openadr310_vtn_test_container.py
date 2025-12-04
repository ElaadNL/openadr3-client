from pathlib import Path
import re
from types import TracebackType
from typing import Any, Self

from testcontainers.core.container import DockerContainer, LogMessageWaitStrategy
from testcontainers.core.network import Network
from testcontainers.mqtt import MosquittoContainer

class OpenADR310VtnTestContainer:
    """A test container for an OpenLeadr-rs VTN (OpenADR 3.0.1) with a PostgreSQL testcontainer dependency."""

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
        Initialize the VTN test container with its PostgreSQL dependency.

        Args:
            oauth_token_endpoint (str): The OAuth token endpoint URL for the VTN to use for token validation.
            oauth_jwks_url (str): The OAuth JWKS URL for the VTN to use for token validation.
            vtn_reference_image (str, optional): The Docker image reference for the VTN. Defaults to "ghcr.io/nicburgt/oadr310-vtn-test:latest".
            vtn_port (int, optional): The port on which the VTN will listen. Defaults to 8080.
            **kwargs: Additional arguments to pass to the DockerContainer constructor.

        """
        self._vtn_port = vtn_port

        if network is None:
            self._internal_network = True
            self._network = Network()
        else:
            self._internal_network = False
            self._network = network

        # Initialize MQTT container, which is required by the VTN.
        self._mqtt = (
            MosquittoContainer(
                image="eclipse-mosquitto:2.0.22",
            )
            .with_network(self._network)
            .with_network_aliases("mqttbroker")
            .waiting_for(LogMessageWaitStrategy(re.compile(r"mosquitto version .* running")))
        )

        tests_root_dir = Path(__file__).resolve().parent
        cert_dir = tests_root_dir / "certs" / "oadr310" / "vtn"

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
            .with_volume_mapping(host=str(cert_dir), container="/vtn_certs", mode="ro")
            .waiting_for(LogMessageWaitStrategy(re.compile(r'.*ListStore\.__init__\(\).*'), re.DOTALL))
        )

    def start(self) -> Self:
        """Start both containers and wait for them to be ready."""
        if self._internal_network:
            # Internal network, so we must create the network manually.
            self._network.create()

        self._mqtt.start()

        # Configure the VTN with the MQTT broker URL prior to starting it.
        self._vtn \
            .with_env("MQTT_VTN_BROKER_IP", "mqttbroker") \
            .with_env("MQTT_VTN_BROKER_PORT", self._mqtt.MQTT_PORT) \
            .with_env("MQTT_CLIENT_BROKER_HOST", "mqttbroker") \
            .with_env("MQTT_CLIENT_BROKER_PORT", self._mqtt.MQTT_PORT) \
            .start()
        
        return self

    def get_base_url(self) -> str:
        """Get the base URL for the VTN."""
        return f"https://localhost:{self._vtn.get_exposed_port(self._vtn_port)}/openadr3/3.1.0"
    
    def get_mqtt_broker_url(self) -> str:
        """Get the MQTT broker URL for the VTN."""
        return f"mqtt://localhost:{self._mqtt.get_exposed_port(1883)}"

    def stop(self) -> None:
        """Stop the openleadr test container and its dependencies."""
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
