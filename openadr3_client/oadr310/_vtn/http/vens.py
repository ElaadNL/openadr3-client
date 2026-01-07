"""Implements the communication with the vens interface of an OpenADR 3 VTN."""

from pydantic.type_adapter import TypeAdapter

from openadr3_client._auth.token_manager import OAuthTokenManagerConfig
from openadr3_client.logging import logger
from openadr3_client.oadr310._vtn.http.http_interface import AuthenticatedHttpInterface
from openadr3_client.oadr310._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.oadr310._vtn.interfaces.vens import ReadOnlyVensInterface, ReadWriteVensInterface, WriteOnlyVensInterface
from openadr3_client.oadr310.models.ven.ven import DeletedVen, ExistingVen, NewVen, VenUpdate

BASE_PREFIX = "vens"


class VensReadOnlyHttpInterface(ReadOnlyVensInterface, AuthenticatedHttpInterface):
    """Implements the read communication with the ven HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, config=config, verify_tls_certificate=verify_tls_certificate)

    def get_vens(self, ven_name: str | None, target: TargetFilter | None, pagination: PaginationFilter | None) -> tuple[ExistingVen, ...]:
        """
        Retrieve vens from the VTN.

        Args:
            ven_name (Optional[str]): The ven name to filter on.
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.

        """
        query_params: dict = {}

        if target:
            query_params |= target.model_dump(by_alias=True, mode="json")

        if pagination:
            query_params |= pagination.model_dump(by_alias=True, mode="json")

        if ven_name:
            query_params |= {"venName": ven_name}

        logger.debug(f"Ven - Performing get_vens request with query params: {query_params}")

        response = self.session.get(f"{self.base_url}/{BASE_PREFIX}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingVen])
        return tuple(adapter.validate_python(response.json()))

    def get_ven_by_id(self, ven_id: str) -> ExistingVen:
        """
        Retrieves a ven by the ven identifier.

        Raises an error if the ven could not be found.

        Args:
            ven_id (str): The ven identifier to retrieve.

        """
        response = self.session.get(f"{self.base_url}/{BASE_PREFIX}/{ven_id}")
        response.raise_for_status()

        return ExistingVen.model_validate(response.json())


class VensWriteOnlyHttpInterface(WriteOnlyVensInterface, AuthenticatedHttpInterface):
    """Implements the write communication with the ven HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, config=config, verify_tls_certificate=verify_tls_certificate)

    def create_ven(self, new_ven: NewVen) -> ExistingVen:
        """
        Creates a ven from the new ven.

        Returns the created report response from the VTN as an ExistingReport.

        Args:
            new_ven (NewVen): The new ven to create.

        """
        with new_ven.with_creation_guard():
            response = self.session.post(f"{self.base_url}/{BASE_PREFIX}", json=new_ven.model_dump(by_alias=True, mode="json"))
            response.raise_for_status()
            return ExistingVen.model_validate(response.json())

    def update_ven_by_id(self, ven_id: str, updated_ven: VenUpdate) -> ExistingVen:
        """
        Update the ven with the ven identifier in the VTN.

        If the ven id does not match the id in the existing ven, an error is
        raised.

        Returns the updated ven response from the VTN.

        Args:
            ven_id (str): The identifier of the ven to update.
            updated_ven (ExistingVen): The ven update to apply.

        """
        # No lock on the ExistingVen type exists similar to the creation guard of a NewVen.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = self.session.put(f"{self.base_url}/{BASE_PREFIX}/{ven_id}", json=updated_ven.model_dump(by_alias=True, mode="json"))
        response.raise_for_status()
        return ExistingVen.model_validate(response.json())

    def delete_ven_by_id(self, ven_id: str) -> DeletedVen:
        """
        Delete the ven with the identifier in the VTN.

        Args:
            ven_id (str): The identifier of the ven to delete.

        """
        response = self.session.delete(f"{self.base_url}/{BASE_PREFIX}/{ven_id}")
        response.raise_for_status()

        return DeletedVen.model_validate(response.json())


class VensHttpInterface(ReadWriteVensInterface, VensReadOnlyHttpInterface, VensWriteOnlyHttpInterface):
    """Implements the read and write communication with the ven HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str, config: OAuthTokenManagerConfig, *, verify_tls_certificate: bool | str = True) -> None:
        super().__init__(base_url=base_url, config=config, verify_tls_certificate=verify_tls_certificate)
