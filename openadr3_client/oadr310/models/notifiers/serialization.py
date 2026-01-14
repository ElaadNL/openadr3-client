# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from enum import StrEnum


class NotifierSerialization(StrEnum):
    """Enumeration of the serialization allowed by the notifier."""

    JSON = "JSON"
