from types import TracebackType
from typing import Any, Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.mqtt import MosquittoContainer

class OpenADR310VtnTestContainer:
    """A test container for an OpenLeadr-rs VTN (OpenADR 3.0.1) with a PostgreSQL testcontainer dependency."""

    def __init__(
        self,
        vtn_reference_image: str = "ghcr.io/nicburgt/oadr310-vtn-test:latest",
        vtn_port: int = 3005,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Initialize the VTN test container with its PostgreSQL dependency.

        Args:
            vtn_reference_image (str, optional): The Docker image reference for the VTN. Defaults to "ghcr.io/nicburgt/oadr310-vtn-test:latest".
            vtn_port (int, optional): The port on which the VTN will listen. Defaults to 3005.
            **kwargs: Additional arguments to pass to the DockerContainer constructor.

        """
        self._vtn_port = vtn_port

        # Create a network for the containers to communicate on.
        self._network = Network()

        # Initialize MQTT container, which is required by the VTN.
        self._mqtt = (
            MosquittoContainer(
                image="eclipse-mosquitto:2.0.22",
            )
            .with_network(self._network)
            .with_network_aliases("mqttbroker")
        )

        # Initialize VTN container with the static environment variables.
        self._vtn = (
            DockerContainer(vtn_reference_image, **kwargs)
            .with_kwargs(platform="linux/amd64")
            .with_network(self._network)
            .with_exposed_ports(self._vtn_port)
            # Set MQTT client broker port of reference VTN to the exposed port of the non encrypted MQTT broker port in the container.
            .with_env("MQTT_CLIENT_BROKER_PORT", self._mqtt.get_exposed_port(1883))
            # Use network alias to communicate with MQTT broker from VTN (same docker network).
            .with_env("MQTT_CLIENT_BROKER_HOST", "mqttbroker")
        )

    def start(self) -> Self:
        """Start both containers and wait for them to be ready."""
        self._network.create()

        self._mqtt.start()
        # Configure the VTN with the database URL prior to starting it.
        self._vtn.start()
        return self

    def get_base_url(self) -> str:
        """Get the base URL for the VTN."""
        return f"http://localhost:{self._vtn.get_exposed_port(self._vtn_port)}/openadr3/3.1.0"
    
    def get_mqtt_broker_url(self) -> str:
        """Get the MQTT broker URL for the VTN."""
        return f"mqtt://localhost:{self._mqtt.get_exposed_port(1883)}"

    def stop(self) -> None:
        """Stop the openleadr test container and its dependencies."""
        self._vtn.stop()
        self._mqtt.stop()
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
