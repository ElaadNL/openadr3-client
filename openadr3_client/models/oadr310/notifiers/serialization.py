from enum import Enum


class NotifierSerialization(str, Enum):
    """Enumeration of the serialization allowed by the notifier."""

    JSON = "JSON"
