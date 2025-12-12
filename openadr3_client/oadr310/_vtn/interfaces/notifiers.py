"""Implements the abstract base classes for the notifiers VTN interface."""

from abc import ABC, abstractmethod

from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import MqttTopicInformation
from openadr3_client.oadr310.models.notifiers.response import NotifierDetails


class ReadOnlyMqttNotifierInterface(ABC):
    """Abstract class which contains the interface for read only methods of the VTN MQTT notifier module."""

    @abstractmethod
    def get_program_topics(self) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on programs.

        Returns:
            MqttTopicInformation: Information on the binding topic names for programs.

        """
        ...

    @abstractmethod
    def get_program_topics_for_id(self, program_id: str) -> MqttTopicInformation:
        """
        List all MQTT binding topic names for operations on a specific program.

        Args:
            program_id (str): The program ID to retrieve binding topics for.

        Returns:
            MqttTopicInformation: Information on the binding topic names for the specific program.

        """
        ...

    @abstractmethod
    def get_event_topics(self) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on events.

        Returns:
            MqttTopicInformation: Information on the binding topic names for events.

        """
        ...

    @abstractmethod
    def get_event_topics_for_program(self, program_id: str) -> MqttTopicInformation:
        """
        List all MQTT binding topic names for operations on events of a specific program.

        Args:
            program_id (str): The program ID to retrieve binding topics of events for.

        Returns:
            MqttTopicInformation: Information on the binding topic names for the events belonging to the specified program.

        """
        ...

    @abstractmethod
    def get_report_topics(self) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on reports.

        Returns:
            MqttTopicInformation: Information on the binding topic names for reports.

        """
        ...

    @abstractmethod
    def get_subscription_topics(self) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on subscriptions.

        Returns:
            MqttTopicInformation: Information on the binding topic names for subscriptions.

        """
        ...

    @abstractmethod
    def get_ven_topics(self) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on vens.

        Returns:
            MqttTopicInformation: Information on the binding topic names for vens.

        """
        ...

    @abstractmethod
    def get_ven_topics_for_id(self, ven_id: str) -> MqttTopicInformation:
        """
        List all MQTT binding topic names for operations on a specific ven.

        Args:
            ven_id (str): The ven ID to retrieve binding topics for.

        Returns:
            MqttTopicInformation: Information on the binding topic names for the specific ven.

        """
        ...

    @abstractmethod
    def get_resource_topics(self) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on resources.

        Returns:
            MqttTopicInformation: Information on the binding topic names for resources.

        """
        ...

    @abstractmethod
    def get_event_topics_for_ven(self, ven_id: str) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on events belonging to a specific VEN.

        Args:
            ven_id (str): The ven ID to retrieve binding topics for.

        Returns:
            MqttTopicInformation: Information on the binding topic names for events of a specific VEN.

        """
        ...

    @abstractmethod
    def get_program_topics_for_ven(self, ven_id: str) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on programs belonging to a specific VEN.

        Args:
            ven_id (str): The ven ID to retrieve binding topics for.

        Returns:
            MqttTopicInformation: Information on the binding topic names for programs of a specific VEN.

        """
        ...

    @abstractmethod
    def get_resource_topics_for_ven(self, ven_id: str) -> MqttTopicInformation:
        """
        List all MQTT notified topic names for operations on resources belonging to a specific VEN.

        Args:
            ven_id (str): The ven ID to retrieve binding topics for.

        Returns:
            MqttTopicInformation: Information on the binding topic names for resources of a specific VEN.

        """
        ...


class ReadOnlyNotifierInterface(ABC):
    """Abstract class which contains the interface for read only methods of the VTN notifier module."""

    @abstractmethod
    def get_notifiers(self) -> NotifierDetails:
        """Retrieve the notifiers supported by this VTN."""
        ...
