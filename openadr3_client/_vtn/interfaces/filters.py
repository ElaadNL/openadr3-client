"""Module containing common filters for VTN requests."""

from openadr3_client.models._base_model import BaseModel


class TargetFilter(BaseModel):
    """Represents a single target filter on a request to the VTN."""

    targets: list[str]
    """The targets to filter on.

    targets being filtered on are treated as a logical AND as per the OpenADR3 specification.
    Meaning that all the targets being filtered on MUST be present in the targets array of the OpenADR object being
    returned."""


class PaginationFilter(BaseModel):
    """Represents a pagination filter on a request to the VTN."""

    skip: int
    """The number of records to skip for pagination."""
    limit: int
    """The maximum number of records to return."""
