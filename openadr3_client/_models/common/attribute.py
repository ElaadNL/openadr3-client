# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the domain models related to attributes."""

from openadr3_client._models.common.value_map import ValueMap


class Attribute[T](ValueMap[str, T]):
    """Class representing an attribute."""
