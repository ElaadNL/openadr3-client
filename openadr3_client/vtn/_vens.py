"""Implements the communication with the vens interface of an OpenADR 3 VTN."""

from dataclasses import asdict

from pydantic.type_adapter import TypeAdapter

from openadr3_client.domain.ven.resource import ExistingResource
from openadr3_client.domain.ven.ven import ExistingVen, NewVen
from openadr3_client.vtn.common._authenticated_session import bearer_authenticated_session
from openadr3_client.vtn.common._vtn_interface import _VtnHttpInterface
from openadr3_client.vtn.common.filters import PaginationFilter, TargetFilter

base_prefix = "vens"


class VensReadOnlyInterface(_VtnHttpInterface):
    """Implements the read communication with the ven HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def get_vens(
        self, ven_name: str | None, target: TargetFilter | None, pagination: PaginationFilter | None
    ) -> tuple[ExistingVen, ...]:
        """
        Retrieve vens from the VTN.

        Args:
            ven_name (Optional[str]): The ven name to filter on.
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.

        """
        # Convert the filters to dictionaries and union them. No key clashing can happen, as the properties
        # of the filters are unique.
        query_params = (
            asdict(target)
            if target
            else {} | asdict(pagination)
            if pagination
            else {} | {"venName": ven_name}
            if ven_name
            else {}
        )

        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingVen])
        return tuple(adapter.validate_json(response.json()))

    def get_ven_by_id(self, ven_id: str) -> ExistingVen:
        """
        Retrieves a ven by the ven identifier.

        Raises an error if the ven could not be found.

        Args:
            ven_id (str): The ven identifier to retrieve.

        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{ven_id}")
        response.raise_for_status()

        return ExistingVen.model_validate_json(response.json())

    def get_ven_resources(
        self,
        ven_id: str,
        resource_name: str | None,
        target: TargetFilter | None,
        pagination: PaginationFilter | None,
    ) -> tuple[ExistingResource, ...]:
        """
        Retrieves a list of resources belonging to the ven with the given ven identifier.

        Args:
            ven_id (str): The ven identifier to retrieve.
            resource_name (Optional[str]): The name of the resource to filter on.
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.

        """
        query_params = (
            asdict(target)
            if target
            else {} | asdict(pagination)
            if pagination
            else {} | {"resourceName": resource_name}
            if resource_name
            else {}
        )

        response = bearer_authenticated_session.get(
            f"{self.base_url}/{base_prefix}/{ven_id}/resources", params=query_params
        )
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingResource])
        return tuple(adapter.validate_json(response.json()))

    def get_ven_resource_by_id(self, ven_id: str, resource_id: str) -> ExistingResource:
        """
        Retrieves a resource by the resource identifier belonging to the ven with the given ven identifier.

        Args:
            ven_id (str): The ven identifier to retrieve.
            resource_id (str): The identifier of the resource to retrieve.

        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{ven_id}/resources/{resource_id}")
        response.raise_for_status()

        return ExistingResource.model_validate_json(response.json())


class VensWriteOnlyInterface(_VtnHttpInterface):
    """Implements the write communication with the ven HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def create_report(self, new_ven: NewVen) -> ExistingVen:
        """
        Creates a ven from the new ven.

        Returns the created report response from the VTN as an ExistingReport.

        Args:
            new_ven (NewVen): The new ven to create.

        """
        with new_ven.with_creation_guard():
            response = bearer_authenticated_session.post(
                f"{self.base_url}/{base_prefix}", data=new_ven.model_dump_json()
            )
            response.raise_for_status()
            return ExistingVen.model_validate_json(response.json())

    def update_report_by_id(self, ven_id: str, updated_ven: ExistingVen) -> ExistingVen:
        """
        Update the ven with the ven identifier in the VTN.

        If the ven id does not match the id in the existing ven, an error is
        raised.

        Returns the updated ven response from the VTN.

        Args:
            ven_id (str): The identifier of the ven to update.
            updated_ven (ExistingVen): The updated ven.

        """
        if ven_id != updated_ven.id:
            exc_msg = "Ven id does not match ven id of updated ven object."
            raise ValueError(exc_msg)

        # No lock on the ExistingVen type exists similar to the creation guard of a NewVen.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(
            f"{self.base_url}/{base_prefix}/{ven_id}", data=updated_ven.model_dump_json()
        )
        response.raise_for_status()
        return ExistingVen.model_validate_json(response.json())

    def delete_ven_by_id(self, ven_id: str) -> None:
        """
        Delete the ven with the identifier in the VTN.

        Args:
            ven_id (str): The identifier of the ven to delete.

        """
        response = bearer_authenticated_session.delete(f"{self.base_url}/{base_prefix}/{ven_id}")
        response.raise_for_status()

    def update_ven_resource_by_id(
        self, ven_id: str, resource_id: str, updated_resource: ExistingResource
    ) -> ExistingResource:
        """
        Update the resource with the resource identifier in the VTN.

        If the ven id does not match the ven_id in the existing resource, an error is
        raised.

        If the resource id does not match the id in the existing resource, an error is raised.

        Returns the updated resource response from the VTN.

        Args:
            ven_id (str): The identifier of the ven the resource belongs to.
            resource_id (str): The identifier of the resource to update.
            updated_resource (ExistingResource): The updated resource.

        """
        if ven_id != updated_resource.ven_id:
            exc_msg = "Ven id does not match ven id of updated resource object."
            raise ValueError(exc_msg)

        if resource_id != updated_resource.id:
            exc_msg = "Resource id does not match id of updated resource object."
            raise ValueError(exc_msg)

        # No lock on the ExistingResource type exists similar to the creation guard of a NewResource.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(
            f"{self.base_url}/{base_prefix}/{ven_id}", data=updated_resource.model_dump_json()
        )
        response.raise_for_status()
        return ExistingResource.model_validate_json(response.json())

    def delete_ven_resource_by_id(self, ven_id: str, resource_id: str) -> None:
        """
        Delete the resource with the resource identifier in the VTN.

        Args:
            ven_id (str): The identifier of the ven the resource belongs to.
            resource_id (str): The identifier of the resource to delete.

        """
        response = bearer_authenticated_session.delete(
            f"{self.base_url}/{base_prefix}/{ven_id}/resources/{resource_id}"
        )
        response.raise_for_status()


class VensInterface(VensReadOnlyInterface, VensWriteOnlyInterface):
    """Implements the read and write communication with the ven HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
