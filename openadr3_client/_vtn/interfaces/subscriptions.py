"""Implements the abstract base class for the subscriptions VTN interfaces."""

from abc import ABC, abstractmethod

from openadr3_client._vtn.interfaces.filters import PaginationFilter, TargetFilter
from openadr3_client.models.subscriptions.subscription import ExistingSubscription, NewSubscription, Object


class ReadOnlySubscriptionsInterface(ABC):
    """Abstract class which contains the interface for read only methods of subscriptions."""

    @abstractmethod
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

    @abstractmethod
    def get_subscription_by_id(self, subscription_id: str) -> ExistingSubscription:
        """
        Retrieves a subscription by the subscription identifier.

        Raises an error if the subscription could not be found.

        Args:
            subscription_id (str): The subscription identifier to retrieve.

        """


class WriteOnlySubscriptionsInterface(ABC):
    """Abstract class which contains the interface for write only methods of subscriptions."""

    @abstractmethod
    def create_subscription(self, new_subscription: NewSubscription) -> ExistingSubscription:
        """
        Creates a subscription from the new subscription.

        Returns the created subscription response from the VTN as an ExistingSubscription.

        Args:
            new_subscription (ExistingSubscription): The new subscription to create.

        """

    @abstractmethod
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

    @abstractmethod
    def delete_subscription_by_id(self, subscription_id: str) -> None:
        """
        Delete the subscription with the identifier in the VTN.

        Args:
            subscription_id (str): The identifier of the subscription to delete.

        """


class ReadWriteSubscriptionsInterface(ReadOnlySubscriptionsInterface, WriteOnlySubscriptionsInterface):
    """Class which allows both read and write access on the resource."""
