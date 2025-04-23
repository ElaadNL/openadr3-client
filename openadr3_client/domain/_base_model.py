from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, field_validator
from pydantic.alias_generators import to_camel


class BaseModel(PydanticBaseModel):
    """Base model for all API models."""

    @field_validator("*")
    @classmethod
    def empty_str_to_none(cls, v: str) -> str | None:
        """Pydantic validator that converts empty strings to None."""
        if v == "":
            return None
        return v

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        frozen=True,  # All domain models are considered immutable.
    )
