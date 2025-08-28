from abc import abstractmethod

from pydantic import ValidationError, model_validator

from openadr3_client.models._base_model import BaseModel
from openadr3_client.plugin import ValidatorPluginRegistry


class ValidatableModel(BaseModel):
    """Base class for all models that should support dynamic validators."""

    @model_validator(mode="after")
    def run_dynamic_validators(self) -> "ValidatableModel":
        """Runs validators from plugins registered in the ValidatorPluginRegistry class."""
        current_value = self

        # Run plugin-based validators
        for validator in ValidatorPluginRegistry.get_model_validators(self.__class__):
            try:
                validator.validate(current_value)
            except (ValueError, ValidationError) as e:
                # Create a custom ValueError that preserves the original error
                # but includes validator metadata
                validator_id = validator.get_validator_id()

                # Create a new error with the same message but add validator info
                error = ValueError(f"Validation error from plugin validator {validator_id}: {e!s}")
                raise error from e

        return self


class OpenADRResource(ValidatableModel):
    """Base model for all OpenADR resources."""

    @property
    @abstractmethod
    def name(self) -> str | None:
        """Helper method to get the name field of the model."""
