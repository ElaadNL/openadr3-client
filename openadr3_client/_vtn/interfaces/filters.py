"""Module containing common filters for VTN requests."""

from openadr3_client.models._base_model import BaseModel


class TargetFilter(BaseModel):
    """Represents a single target filter on a request to the VTN."""

    target_type: str
    """The target type to filter on."""
    target_values: list[str]
    """The target values to filter on, treated as a logical OR as per the OpenADR3 specification."""


class PaginationFilter(BaseModel):
    """Represents a pagination filter on a request to the VTN."""

    skip: int
    """The number of records to skip for pagination."""
    limit: int
    """The maximum number of records to return."""
