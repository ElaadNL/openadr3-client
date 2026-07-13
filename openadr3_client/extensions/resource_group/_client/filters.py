# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Filters for resource group VTN requests."""

from openadr3_client._models._base_model import BaseModel


class TargetFilter(BaseModel):
    """A target filter on a resource group request. Targets are treated as a logical AND."""

    targets: list[str]


class PaginationFilter(BaseModel):
    """A pagination filter on a resource group request."""

    skip: int
    limit: int
