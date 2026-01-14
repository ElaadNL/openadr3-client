# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from enum import StrEnum


class OADRVersion(StrEnum):
    """The OpenADR Versions supported by this library."""

    OADR_301 = "oadr301"
    OADR_310 = "oadr310"
