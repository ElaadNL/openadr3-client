"""Implements the communication with the subscriptions interface of an OpenADR 3 VTN."""

from pydantic.type_adapter import TypeAdapter

from openadr3_client._vtn.http.common._authenticated_session import bearer_authenticated_session
from openadr3_client._vtn.http.http_interface import HttpInterface
from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client._vtn.interfaces.subscriptions import (
    ReadOnlySubscriptionsInterface,
    ReadWriteSubscriptionsInterface,
    WriteOnlySubscriptionsInterface,
)
from openadr3_client.logging import logger
from openadr3_client.models.subscriptions.subscription import ExistingSubscription, NewSubscription, Object

base_prefix = "subscriptions"


class SubscriptionsReadOnlyHttpInterface(ReadOnlySubscriptionsInterface, HttpInterface):
    """Implements the read communication with the subscriptions HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def get_subscriptions(
        self,
        pagination: PaginationFilter | None,
        target: TargetFilter | None,
        program_id: str | None,
        client_name: str | None,
        objects: tuple[Object, ...] | None,
    ) -> tuple[ExistingSubscription, ...]:
        """
        Retrieve subscriptions from the VTN.

        Args:
            target (Optional[TargetFilter]): The target to filter on.
            pagination (Optional[PaginationFilter]): The pagination to apply.
            program_id (str): The program id to filter on.
            event_id (str): The event id to filter on.
            client_name (str): The client name to filter on.
            objects: (Optional[Tuple[Object, ...]]): The objects to filter on.

        """
        # Convert the filters to dictionaries and union them. No key clashing can happen, as the properties
        # of the filters are unique.
        query_params: dict = {}

        if target:
            query_params |= target.model_dump(by_alias=True, mode="json")

        if pagination:
            query_params |= pagination.model_dump(by_alias=True, mode="json")

        if program_id:
            query_params |= {"programID": program_id}

        if client_name:
            query_params |= {"clientName": client_name}

        if objects:
            query_params |= {"objects": [objects]}

        logger.debug("Subscriptions - Performing get_subscriptions request with query params: %s", query_params)

        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(list[ExistingSubscription])
        return tuple(adapter.validate_python(response.json()))

    def get_subscription_by_id(self, subscription_id: str) -> ExistingSubscription:
        """
        Retrieves a subscription by the subscription identifier.

        Raises an error if the subscription could not be found.

        Args:
            subscription_id (str): The subscription identifier to retrieve.

        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{subscription_id}")
        response.raise_for_status()

        return ExistingSubscription.model_validate(response.json())


class SubscriptionsWriteOnlyHttpInterface(WriteOnlySubscriptionsInterface, HttpInterface):
    """Implements the write communication with the subscriptions HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def create_subscription(self, new_subscription: NewSubscription) -> ExistingSubscription:
        """
        Creates a subscription from the new subscription.

        Returns the created subscription response from the VTN as an ExistingSubscription.

        Args:
            new_subscription (ExistingSubscription): The new subscription to create.

        """
        with new_subscription.with_creation_guard():
            response = bearer_authenticated_session.post(
                f"{self.base_url}/{base_prefix}", json=new_subscription.model_dump(by_alias=True, mode="json")
            )
            response.raise_for_status()
            return ExistingSubscription.model_validate(response.json())

    def update_subscription_by_id(
        self, subscription_id: str, updated_subscription: ExistingSubscription
    ) -> ExistingSubscription:
        """
        Update the subscription with the subscription identifier in the VTN.

        If the subscription id does not match the id in the existing subscription, an error is
        raised.

        Returns the updated subscription response from the VTN.

        Args:
            subscription_id (str): The identifier of the subscription to update.
            updated_subscription (ExistingSubscription): The updated subscription.

        """
        if subscription_id != updated_subscription.id:
            exc_msg = "Subscription id does not match subscription id of updated subscription object."
            raise ValueError(exc_msg)

        # No lock on the ExistingSubscription type exists similar to the creation guard of a NewSubscription.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(
            f"{self.base_url}/{base_prefix}/{subscription_id}",
            json=updated_subscription.model_dump(by_alias=True, mode="json"),
        )
        response.raise_for_status()
        return ExistingSubscription.model_validate(response.json())

    def delete_subscription_by_id(self, subscription_id: str) -> None:
        """
        Delete the subscription with the identifier in the VTN.

        Args:
            subscription_id (str): The identifier of the subscription to delete.

        """
        response = bearer_authenticated_session.delete(f"{self.base_url}/{base_prefix}/{subscription_id}")
        response.raise_for_status()


class SubscriptionsHttpInterface(
    ReadWriteSubscriptionsInterface, SubscriptionsReadOnlyHttpInterface, SubscriptionsWriteOnlyHttpInterface
):
    """Implements the read and write communication with the subscriptions HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
