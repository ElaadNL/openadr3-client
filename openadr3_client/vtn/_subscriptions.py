"""Implements the communication with the subscriptions interface of an OpenADR 3 VTN."""
from typing import List, Optional, Tuple

from pydantic.type_adapter import TypeAdapter
from openadr3_client.domain.subscriptions.subscription import Object
from openadr3_client.vtn.common._vtn_interface import VtnHttpInterface
from openadr3_client.vtn.common.filters import PaginationFilter, TargetFilter
from openadr3_client.domain.subscriptions.subscription import ExistingSubscription, NewSubscription
from openadr3_client.vtn.common._authenticated_session import bearer_authenticated_session

from dataclasses import asdict

base_prefix = "subscriptions"

class SubscriptionsReadOnlyInterface(VtnHttpInterface):
    """Implements the read communication with the subscriptions HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url):
        super().__init__(base_url)

    def get_subscriptions(self,
                          pagination: Optional[PaginationFilter],
                          target: Optional[TargetFilter],
                          program_id: Optional[str],
                          client_name: Optional[str],
                          objects: Optional[Tuple[Object, ...]]) -> Tuple[ExistingSubscription, ...]:
        """Retrieve subscriptions from the VTN.
        
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
        query_params = \
            asdict(pagination) if pagination else {} \
            | asdict(target) if target else {} \
            | {"programID": program_id} if program_id else {} \
            | {"clientName": client_name} if client_name else {} \
            | {"objects": [ objects ]} if objects else {} 

        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}", params=query_params)
        response.raise_for_status()

        adapter = TypeAdapter(List[ExistingSubscription])
        return tuple(adapter.validate_json(response.json()))

    def get_subscription_by_id(self, subscription_id: str) -> ExistingSubscription:
        """Retrieves a subscription by the subscription identifier.
        
        Raises an error if the subscription could not be found.
        
        Args:
            subscription_id (str): The subscription identifier to retrieve.
        """
        response = bearer_authenticated_session.get(f"{self.base_url}/{base_prefix}/{subscription_id}")
        response.raise_for_status()

        return ExistingSubscription.model_validate_json(response.json())

class SubscriptionsWriteOnlyInterface(VtnHttpInterface):
    """Implements the write communication with the subscriptions HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url):
        super().__init__(base_url)

    def create_subscription(self, new_subscription: NewSubscription) -> ExistingSubscription:
        """Creates a subscription from the new subscription.
        
        Returns the created subscription response from the VTN as an ExistingSubscription.
        
        Args:
            new_subscription (ExistingSubscription): The new subscription to create.
        """
        with new_subscription.with_creation_guard():
            response = bearer_authenticated_session.post(f"{self.base_url}/{base_prefix}", data=new_subscription.model_dump_json())
            response.raise_for_status()
            return ExistingSubscription.model_validate_json(response.json())

    def update_subscription_by_id(self, subscription_id: str, updated_subscription: ExistingSubscription) -> ExistingSubscription:
        """Update the subscription with the subscription identifier in the VTN.

        If the subscription id does not match the id in the existing subscription, an error is
        raised.

        Returns the updated subscription response from the VTN.

        Args:
            subscription_id (str): The identifier of the subscription to update.
            updated_subscription (ExistingSubscription): The updated subscription.
        """
        if subscription_id != updated_subscription.id:
            raise ValueError("Subscription id does not match subscription id of updated subscription object.")
        
        # No lock on the ExistingSubscription type exists similar to the creation guard of a NewSubscription.
        # Since calling update with the same object multiple times is an idempotent action that does not
        # result in a state change in the VTN.
        response = bearer_authenticated_session.put(f"{self.base_url}/{base_prefix}/{subscription_id}",
                                                    data=updated_subscription.model_dump_json())
        response.raise_for_status()
        return ExistingSubscription.model_validate_json(response.json())

    def delete_subscription_by_id(self, subscription_id: str) -> None:
        """Delete the subscription with the identifier in the VTN.

        Args:
            subscription_id (str): The identifier of the subscription to delete.
        """
        response = bearer_authenticated_session.delete(f"{self.base_url}/{base_prefix}/{subscription_id}")
        response.raise_for_status()

class SubscriptionsInterface(SubscriptionsReadOnlyInterface, SubscriptionsWriteOnlyInterface):
    """Implements the read and write communication with the subscriptions HTTP interface of an OpenADR 3 VTN."""

    def __init__(self, base_url):
        super().__init__(base_url)