# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""HTTP communication with the /resource_groups interface of an NLFlex VTN."""

from pydantic.type_adapter import TypeAdapter

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.extensions.resource_group._client.filters import PaginationFilter, TargetFilter
from openadr3_client.extensions.resource_group._client.http_interface import AuthenticatedHttpInterface
from openadr3_client.extensions.resource_group._client.interfaces import (
    ReadOnlyResourceGroupsInterface,
    ReadWriteResourceGroupsInterface,
    WriteOnlyResourceGroupsInterface,
)
from openadr3_client.extensions.resource_group.models.resource_group import (
    DeletedResourceGroup,
    ExistingResourceGroup,
    NewResourceGroup,
    ResourceGroupUpdate,
)

BASE_PREFIX = "resource_groups"


class ResourceGroupsReadOnlyHttpInterface(ReadOnlyResourceGroupsInterface, AuthenticatedHttpInterface):
    """Read-only HTTP communication with the /resource_groups interface."""

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
        *,
        verify_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
    ) -> None:
        super().__init__(
            base_url=base_url,
            config=config,
            verify_tls_certificate=verify_tls_certificate,
            allow_insecure_http=allow_insecure_http,
        )

    def get_resource_groups(
        self,
        resource_group_name: str | None = None,
        target: TargetFilter | None = None,
        pagination: PaginationFilter | None = None,
    ) -> tuple[ExistingResourceGroup, ...]:
        query_params: dict = {}
        if target:
            query_params |= target.model_dump(by_alias=True, mode="json")
        if pagination:
            query_params |= pagination.model_dump(by_alias=True, mode="json")
        if resource_group_name:
            query_params |= {"resourceGroupName": resource_group_name}

        response = self.session.get(f"{self.base_url}/{BASE_PREFIX}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingResourceGroup])
        return tuple(adapter.validate_python(response.json()))

    def get_resource_group_by_id(self, resource_group_id: str) -> ExistingResourceGroup:
        response = self.session.get(f"{self.base_url}/{BASE_PREFIX}/{resource_group_id}")
        response.raise_for_status()
        return ExistingResourceGroup.model_validate(response.json())


class ResourceGroupsWriteOnlyHttpInterface(WriteOnlyResourceGroupsInterface, AuthenticatedHttpInterface):
    """Write HTTP communication with the /resource_groups interface."""

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
        *,
        verify_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
    ) -> None:
        super().__init__(
            base_url=base_url,
            config=config,
            verify_tls_certificate=verify_tls_certificate,
            allow_insecure_http=allow_insecure_http,
        )

    def create_resource_group(self, new_resource_group: NewResourceGroup) -> ExistingResourceGroup:
        with new_resource_group.with_creation_guard():
            response = self.session.post(
                f"{self.base_url}/{BASE_PREFIX}",
                json=new_resource_group.model_dump(by_alias=True, mode="json"),
            )
            response.raise_for_status()
            return ExistingResourceGroup.model_validate(response.json())

    def update_resource_group_by_id(
        self, resource_group_id: str, updated_resource_group: ResourceGroupUpdate
    ) -> ExistingResourceGroup:
        response = self.session.put(
            f"{self.base_url}/{BASE_PREFIX}/{resource_group_id}",
            json=updated_resource_group.model_dump(by_alias=True, mode="json"),
        )
        response.raise_for_status()
        return ExistingResourceGroup.model_validate(response.json())

    def delete_resource_group_by_id(self, resource_group_id: str) -> DeletedResourceGroup:
        response = self.session.delete(f"{self.base_url}/{BASE_PREFIX}/{resource_group_id}")
        response.raise_for_status()
        return DeletedResourceGroup.model_validate(response.json())


class ResourceGroupsHttpInterface(
    ReadWriteResourceGroupsInterface,
    ResourceGroupsReadOnlyHttpInterface,
    ResourceGroupsWriteOnlyHttpInterface,
):
    """Read and write HTTP communication with the /resource_groups interface."""

    def __init__(
        self,
        base_url: str,
        config: OAuthTokenManagerConfig,
        *,
        verify_tls_certificate: bool | str = True,
        allow_insecure_http: bool = False,
    ) -> None:
        super().__init__(
            base_url=base_url,
            config=config,
            verify_tls_certificate=verify_tls_certificate,
            allow_insecure_http=allow_insecure_http,
        )
