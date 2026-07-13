# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Abstract interfaces for resource group clients (BL read-write, VEN read-only)."""

from abc import ABC, abstractmethod

from openadr3_client.extensions.resource_group._client.filters import PaginationFilter, TargetFilter
from openadr3_client.extensions.resource_group.models.resource_group import (
    DeletedResourceGroup,
    ExistingResourceGroup,
    NewResourceGroup,
    ResourceGroupUpdate,
)


class ReadOnlyResourceGroupsInterface(ABC):
    """Read-only resource group operations. Used by VEN clients (results are obfuscated server-side)."""

    @abstractmethod
    def get_resource_groups(
        self,
        resource_group_name: str | None = None,
        target: TargetFilter | None = None,
        pagination: PaginationFilter | None = None,
    ) -> tuple[ExistingResourceGroup, ...]:
        """Retrieve resource groups, optionally filtered by name, targets, and pagination."""

    @abstractmethod
    def get_resource_group_by_id(self, resource_group_id: str) -> ExistingResourceGroup:
        """Retrieve a single resource group by its id."""


class WriteOnlyResourceGroupsInterface(ABC):
    """Write resource group operations. BL clients only."""

    @abstractmethod
    def create_resource_group(self, new_resource_group: NewResourceGroup) -> ExistingResourceGroup:
        """Create a new resource group."""

    @abstractmethod
    def update_resource_group_by_id(self, resource_group_id: str, updated_resource_group: ResourceGroupUpdate) -> ExistingResourceGroup:
        """Update the resource group with the given id."""

    @abstractmethod
    def delete_resource_group_by_id(self, resource_group_id: str) -> DeletedResourceGroup:
        """Delete the resource group with the given id."""


class ReadWriteResourceGroupsInterface(ReadOnlyResourceGroupsInterface, WriteOnlyResourceGroupsInterface):
    """Read-write resource group operations. Used by BL clients."""
