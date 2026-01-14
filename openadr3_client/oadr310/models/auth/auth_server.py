# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import Field

from openadr3_client._models._base_model import BaseModel


class AuthServerInfo(BaseModel):
    """Represents information related to the authorization service used by the VTN."""

    token_url: str = Field(alias="tokenURL")
    """The URL at which to fetch access tokens with which to authenticate to this VTN."""
