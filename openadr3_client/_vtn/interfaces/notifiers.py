"""Implements the abstract base classes for the notifiers VTN interface."""

from abc import ABC, abstractmethod

from openadr3_client.models.notifiers.mqtt.mqtt import MqttTopicInformation
from openadr3_client.models.notifiers.response import NotifierDetails

class ReadOnlyMqttNotifierInterface(ABC):
    """Abstract class which contains the interface for read only methods of the VTN MQTT notifier module."""

    @abstractmethod
    def get_program_topics(self) -> MqttTopicInformation:
        """List all MQTT notified topic names for operations on programs.
        
        Returns:
            MqttTopicInformation: Information on the binding topic names for programs."""
        ...

    @abstractmethod
    def get_program_topics_for_id(self, program_id: str) -> MqttTopicInformation:
        """List all MQTT binding topic names for operations on a specific program.
        
        Args:
            program_id (str): The program ID to retrieve binding topics for.
            
        Returns:
            MqttTopicInformation: Information on the binding topic names for the specific program."""
        ...

    @abstractmethod
    def get_event_topics(self) -> MqttTopicInformation:
        """List all MQTT notified topic names for operations on events.
        
        Returns:
            MqttTopicInformation: Information on the binding topic names for events."""
        ...

    @abstractmethod
    def get_event_topics_for_id(self, event_id: str) -> MqttTopicInformation:
        """List all MQTT binding topic names for operations on a specific event.
        
        Args:
            event_id (str): The event ID to retrieve binding topics for.
            
        Returns:
            MqttTopicInformation: Information on the binding topic names for the specific event."""
        ...

class ReadOnlyNotifierInterface(ABC):
    """Abstract class which contains the interface for read only methods of the VTN notifier module."""
    
    @abstractmethod
    def get_notifiers(self) -> NotifierDetails:
        """Retrieve the notifiers supported by this VTN."""
        ...

        