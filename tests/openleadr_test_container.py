# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

import threading
import uuid
from collections import deque
from types import TracebackType
from typing import Any, Self

import docker.errors
from testcontainers.core.container import DockerContainer, LogMessageWaitStrategy
from testcontainers.core.network import Network
from testcontainers.postgres import PostgresContainer

_LOG_BUFFER_MAX_LINES = 5_000


class OpenLeadrVtnTestContainer:
    """A test container for an OpenLeadr-rs VTN (OpenADR 3.0.1) with a PostgreSQL testcontainer dependency."""

    def __init__(
        self,
        openleadr_rs_image: str,
        oauth_jwks_url: str,
        oauth_valid_audiences: str,
        oauth_token_url: str,
        network: Network | None = None,
        oauth_key_type: str = "RSA",
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
            oauth_jwks_url (str): The OAuth server JWKS URL. Used by OpenLEADR-rs to validate JWT signatures.
            oauth_valid_audiences (str): The valid audiences for the OAuth token, the provided value must be a
            comma seperated list of valid audiences.
            oauth_token_url (str): The OAuth token endpoint URL. Required by OpenLEADR-rs, also when `OAUTH_TYPE=EXTERNAL`.
            network (Network | None, optional): The Docker network to use. If None, a new network will be created.
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
        self._log_stop_event = threading.Event()
        self._vtn_log_lines: deque[str] = deque(maxlen=_LOG_BUFFER_MAX_LINES)
        self._vtn_log_thread: threading.Thread | None = None
        # Unique alias so multiple VTN instances on the same Docker network don't
        # share a "vtndb" DNS entry and accidentally resolve to each other's Postgres.
        self._postgres_alias = f"vtndb-{uuid.uuid4().hex[:8]}"

        if network is None:
            self._internal_network = True
            self._network = Network()
        else:
            self._internal_network = False
            self._network = network

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
            .with_network_aliases(self._postgres_alias)
            .waiting_for(LogMessageWaitStrategy("database system is ready to accept connections"))
        )

        # Initialize VTN container with the static environment variables.
        self._vtn = (
            DockerContainer(openleadr_rs_image, **kwargs)
            .with_kwargs(platform="linux/amd64")
            .with_network(self._network)
            .with_exposed_ports(self._vtn_port)
            .with_env(key="OAUTH_TYPE", value="EXTERNAL")
            .with_env(key="OAUTH_VALID_AUDIENCES", value=oauth_valid_audiences)
            .with_env(key="OAUTH_KEY_TYPE", value=oauth_key_type)
            .with_env(key="OAUTH_JWKS_LOCATION", value=oauth_jwks_url)
            .with_env(key="OAUTH_TOKEN_URL", value=oauth_token_url)
            .with_env(key="PG_PORT", value=self._postgres.port)
            .with_env(key="PG_DB", value=postgres_db)
            .with_env(key="PG_USER", value=postgres_user)
            .with_env(key="PG_PASSWORD", value=postgres_password)
            .with_env(key="PG_TZ", value="Europe/Amsterdam")
            .with_env(key="RUST_BACKTRACE", value="full")
            .with_env(key="RUST_LOG", value="trace")
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
                # Container may be removed/stopped while following logs.
                return

        self._vtn_log_thread = threading.Thread(target=_run, name="openleadr-rs-vtn-logs", daemon=True)
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

        self._postgres.start()

        # Create the database URL for the VTN. Which can only be determined
        # after the postgres container has started.
        vtn_db_url = (
            self._postgres.get_connection_url(driver=None)
            .replace("postgresql", "postgres")
            .replace("localhost", self._postgres_alias)
            .replace(str(self._postgres.get_exposed_port(self._postgres_port)), "5432")
        )

        # Configure the VTN with the database URL prior to starting it.
        self._vtn.with_env(key="DATABASE_URL", value=vtn_db_url).waiting_for(LogMessageWaitStrategy("pg_advisory_unlock")).start()
        self._start_vtn_log_capture()
        return self

    def get_base_url(self) -> str:
        """Get the base URL for the VTN."""
        return f"http://localhost:{self._vtn.get_exposed_port(self._vtn_port)}"

    def stop(self) -> None:
        """Stop the openleadr test container and its dependencies."""
        self._log_stop_event.set()
        self._vtn.stop()
        self._postgres.stop()
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


class OpenAdr301VtnTestContainer(OpenLeadrVtnTestContainer):
    """A test container for an OpenADR 3.0.1 VTN."""

    def __init__(
        self,
        oauth_jwks_url: str,
        oauth_valid_audiences: str,
        oauth_token_url: str,
        network: Network | None = None,
    ) -> None:
        super().__init__(
            openleadr_rs_image="ghcr.io/openleadr/openleadr-rs:0.1.2",
            oauth_jwks_url=oauth_jwks_url,
            oauth_valid_audiences=oauth_valid_audiences,
            oauth_token_url=oauth_token_url,
            network=network,
        )


class OpenAdr310VtnTestContainer(OpenLeadrVtnTestContainer):
    """A test container for an OpenADR 3.1.0 VTN."""

    def __init__(
        self,
        oauth_jwks_url: str,
        oauth_valid_audiences: str,
        oauth_token_url: str,
        network: Network | None = None,
    ) -> None:
        # TODO(Stijn van Houwelingen): update to latest release once out of development.  # noqa: FIX002, TD003
        super().__init__(
            openleadr_rs_image="ghcr.io/openleadr/openleadr-rs:1769690654-06c15ea",
            oauth_jwks_url=oauth_jwks_url,
            oauth_valid_audiences=oauth_valid_audiences,
            oauth_token_url=oauth_token_url,
            network=network,
        )
