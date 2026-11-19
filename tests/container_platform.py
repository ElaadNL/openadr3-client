# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Helpers for running single-architecture (amd64-only) images in testcontainers, also on arm64 hosts."""

import docker.errors
from testcontainers.core.container import DockerContainer
from testcontainers.core.docker_client import DockerClient

# Platform for images which are only published for amd64. On arm64 hosts (e.g. Apple Silicon)
# these run under emulation.
AMD64_PLATFORM = "linux/amd64"


def ensure_image_for_platform(container: DockerContainer, platform: str = AMD64_PLATFORM) -> None:
    """
    Pull the image of the container for the given platform, if it is not present locally.

    Workaround for testcontainers >= 4.15.0, where `DockerClient.create` pulls missing images without
    the `platform` passed through `with_kwargs`, so the host platform is used instead. This fails for
    amd64-only images on arm64 hosts ("no matching manifest for linux/arm64/v8").
    Introduced in https://github.com/testcontainers/testcontainers-python/pull/976.

    Once the image is present locally, testcontainers skips its own pull, and still creates the
    container with the configured platform.

    Args:
        container: The container whose image should be pulled. It must be configured with
            `with_kwargs(platform=...)` for the same platform.
        platform: The platform to pull the image for.

    """
    client = DockerClient().client
    try:
        client.images.get(container.image)
    except docker.errors.ImageNotFound:
        client.images.pull(container.image, platform=platform)
