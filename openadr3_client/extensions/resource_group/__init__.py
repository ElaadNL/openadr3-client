# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""NLFlex resource group extension — models and a standalone CRUD client."""

from openadr3_client.extensions.resource_group._client.filters import PaginationFilter, TargetFilter
from openadr3_client.extensions.resource_group._client.interfaces import (
    ReadOnlyResourceGroupsInterface,
    ReadWriteResourceGroupsInterface,
)
from openadr3_client.extensions.resource_group.factory import ResourceGroupClientFactory
from openadr3_client.extensions.resource_group.models.resource_group import (
    DeletedResourceGroup,
    ExistingResourceGroup,
    NewResourceGroup,
    ResourceGroupChild,
    ResourceGroupUpdate,
)

__all__ = [
    "DeletedResourceGroup",
    "ExistingResourceGroup",
    "NewResourceGroup",
    "PaginationFilter",
    "ReadOnlyResourceGroupsInterface",
    "ReadWriteResourceGroupsInterface",
    "ResourceGroupChild",
    "ResourceGroupClientFactory",
    "ResourceGroupUpdate",
    "TargetFilter",
]
