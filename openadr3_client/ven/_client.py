# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from openadr3_client.version import OADRVersion


class BaseVirtualEndNodeClient:
    """Base class for virtual end node clients."""

    def __init__(
        self,
        version: OADRVersion,
    ) -> None:
        """
        Initializes the base virtual end node client.

        Args:
            version: The OpenADR version used by this client.

        """
        self.version = version
