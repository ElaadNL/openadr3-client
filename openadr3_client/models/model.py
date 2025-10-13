from abc import abstractmethod

from pydantic import ValidationError, model_validator
from pydantic_core import InitErrorDetails

from openadr3_client.models._base_model import BaseModel
from openadr3_client.plugin import ValidatorPluginRegistry


class ValidatableModel(BaseModel):
    """Base class for all models that should support dynamic validators."""

    @model_validator(mode="after")
    def run_dynamic_validators(self) -> "ValidatableModel":
        """Runs validators from plugins registered in the ValidatorPluginRegistry class."""
        current_value = self
        validation_errors: list[InitErrorDetails] = []

        # Run plugin-based validators and collect all errors
        for validator_info in ValidatorPluginRegistry.get_model_validators(self.__class__):
            validator_errors = validator_info.validate(current_value)
            if validator_errors:
                validation_errors.extend(validator_errors)

        # If any errors were collected, raise a single Pydantic ValidationError
        if validation_errors:
            raise ValidationError.from_exception_data(title=self.__class__.__name__, line_errors=validation_errors)

        return self


class OpenADRResource(ValidatableModel):
    """Base model for all OpenADR resources."""

    @property
    @abstractmethod
    def name(self) -> str | None:
        """Helper method to get the name field of the model."""
