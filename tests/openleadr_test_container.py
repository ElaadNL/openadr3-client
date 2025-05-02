from types import TracebackType
from typing import Any, Self

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer

from openadr3_client.logging import logger


class OpenLeadrVtnTestContainer:
    """A test container for an OpenLeadr-rs VTN with a PostgreSQL testcontainer dependency."""

    def __init__(
        self,
        external_oauth_signing_key_pem_path: str,
        oauth_valid_audiences: str,
        oauth_key_type: str = "RSA",
        openleadr_rs_image: str = "ghcr.io/openleadr/openleadr-rs:latest",
        postgres_image: str = "postgres:16",
        vtn_port: int = 3000,
        postgres_port: int = 5432,
        postgres_user: str = "openadr",
        postgres_password: str = "openadr",  # noqa: S107
        postgres_db: str = "openadr",
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Initialize the VTN test container with its PostgreSQL dependency.

        Args:
            external_oauth_signing_key_pem_path (str): The path to the external OAuth signing public key in PEM format.
            oauth_valid_audiences (str): The valid audiences for the OAuth token, the provided value must be a
            comma seperated list of valid audiences.
            oauth_key_type (str, optional): The type of OAuth key. Defaults to "RSA".
            openleadr_rs_image (str, optional): The image to use for the VTN.
            Defaults to "ghcr.io/openleadr/openleadr-rs:latest".
            postgres_image (str, optional): The image to use for the PostgreSQL container. Defaults to "postgres:16".
            vtn_port (int, optional): The port on which the VTN will listen. Defaults to 3000.
            postgres_port (int, optional): The port for the PostgreSQL container. Defaults to 5432.
            postgres_user (str, optional): PostgreSQL username. Defaults to "openadr".
            postgres_password (str, optional): PostgreSQL password. Defaults to "openadr".
            postgres_db (str, optional): PostgreSQL database name. Defaults to "openadr".
            **kwargs: Additional arguments to pass to the DockerContainer constructor.

        """
        self._vtn_port = vtn_port
        self._postgres_port = postgres_port

        # Create a network for the containers to communicate on.
        self._network = Network()

        # Initialize PostgreSQL container
        self._postgres = (
            PostgresContainer(
                image=postgres_image,
                port=self._postgres_port,
                username=postgres_user,
                password=postgres_password,
                dbname=postgres_db,
            )
            .with_network(self._network)
            .with_network_aliases("vtndb")
        )

        # Initialize VTN container with the static environment variables.
        self._vtn = (
            DockerContainer(openleadr_rs_image, **kwargs)
            .with_network(self._network)
            .with_exposed_ports(self._vtn_port)
            .with_volume_mapping(host=external_oauth_signing_key_pem_path, container="/keys/pub-sign-key.pem")
            .with_env(key="OAUTH_TYPE", value="EXTERNAL")
            .with_env(key="OAUTH_VALID_AUDIENCES", value=oauth_valid_audiences)
            .with_env(key="OAUTH_KEY_TYPE", value=oauth_key_type)
            .with_env(key="OAUTH_PEM", value="/keys/pub-sign-key.pem")
            .with_env(key="PG_PORT", value=self._postgres.port)
            .with_env(key="PG_DB", value=postgres_db)
            .with_env(key="PG_USER", value=postgres_user)
            .with_env(key="PG_PASSWORD", value=postgres_password)
            .with_env(key="PG_TZ", value="Europe/Amsterdam")
            .with_env(key="RUST_BACKTRACE", value="full")
            .with_env(key="RUST_LOG", value="trace")
        )

    def start(self) -> Self:
        """Start both containers and wait for them to be ready."""
        self._network.create()

        self._postgres.start()

        # Create the database URL for the VTN. Which can only be determined
        # after the postgres container has started.
        vtn_db_url = (
            self._postgres.get_connection_url(driver=None)
            .replace("postgresql", "postgres")
            .replace("localhost", "vtndb")
            .replace(self._postgres.get_exposed_port(self._postgres_port), "5432")
        )

        # Configure the VTN with the database URL prior to starting it.
        self._vtn.with_env(key="DATABASE_URL", value=vtn_db_url).start()
        self._wait_for_ready()
        return self

    def _wait_for_ready(self) -> None:
        """Wait for the VTN to be ready to accept connections."""
        try:
            wait_for_logs(self._vtn, "pg_advisory_unlock", timeout=30, raise_on_exit=True)
        except RuntimeError:
            stdout, stderr = self._vtn.get_logs()
            stdout = stdout.decode()
            stderr = stderr.decode()
            logger.error("VTN exited: stdout: %s, stderr: %s", stdout, stderr)
            raise

    def _wait_for_postgres_ready(self) -> None:
        """Wait for the PostgreSQL container to be ready."""
        try:
            wait_for_logs(
                self._postgres, "database system is ready to accept connections", timeout=30, raise_on_exit=True
            )
        except RuntimeError:
            stdout, stderr = self._postgres.get_logs()
            stdout = stdout.decode()
            stderr = stderr.decode()
            logger.error("PostgreSQL exited: stdout: %s, stderr: %s", stdout, stderr)
            raise

    def get_base_url(self) -> str:
        """Get the base URL for the VTN."""
        return f"http://localhost:{self._vtn.get_exposed_port(self._vtn_port)}"

    def stop(self) -> None:
        """Stop the openleadr test container and its dependencies."""
        self._vtn.stop()
        self._postgres.stop()
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
