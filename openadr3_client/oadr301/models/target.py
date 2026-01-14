# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the domain models related to targeting."""

from openadr3_client._models.common.value_map import ValueMap


class Target[T](ValueMap[str, T]):
    """Class representing a target."""
