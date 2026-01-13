# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from openadr3_client.version import OADRVersion


class BaseBusinessLogicClient:
    """Base class for business logic clients."""

    def __init__(
        self,
        version: OADRVersion,
    ) -> None:
        """
        Initializes the base business logic client.

        Args:
            version (OADRVersion): The OpenADR version used by this client.

        """
        self.version = version
