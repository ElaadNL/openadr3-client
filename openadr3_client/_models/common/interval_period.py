"""This module implements the common Interval Period used across OpenADR3 resources."""

from datetime import timedelta

from pydantic import AwareDatetime

from openadr3_client._models._validatable_model import ValidatableModel


class IntervalPeriod(ValidatableModel):
    """
    Defines temporal aspects of intervals.

    A duration of PT0S indicates instantaneous or infinity, depending on payloadType.

    Attributes:
        start: The start time of the interval, must be timezone-aware.
        duration: The duration of the interval.
            PT0S indicates instantaneous or infinity, depending on payloadType.
        randomize_start: Optional randomization window for the start time.
            None indicates no randomization. Defaults to None.

    """

    start: AwareDatetime
    duration: timedelta
    randomize_start: timedelta | None = None
