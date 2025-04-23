"""Implements the communication with the events interface of an OpenADR 3 VTN."""

from typing import Tuple
from openadr3_client.domain.event.event import ExistingEvent


def get_events(self) -> Tuple[ExistingEvent, ...]:
    """Retrieve events from the VTN"""