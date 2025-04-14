from typing import Callable, Dict, Tuple, Type
from pydantic import model_validator
from openadr3_client.domain._base_model import BaseModel


class Model:
    pass


class Field:
    field_name: str

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name


ValidationTarget = Model | Field


class ValidatorRegistry:
    _validators: Dict[
        Type["ValidatableModel"], Dict[ValidationTarget, Tuple[Callable, ...]]
    ] = {}

    @classmethod
    def register(
        self,
        model: Type["ValidatableModel"],
        target: ValidationTarget = Model(),
    ) -> Callable:
        """Decorator to register validators for specific models and fields"""

        def decorator(validator: Callable) -> Callable:
            if target_dict := self._validators.get(model):
                if existing_validators := target_dict.get(target):
                    # Target already exists in the validators for the model, simply
                    # update the validators.
                    new_validators = (validator,) + existing_validators
                    self._validators[model][target] = new_validators
                else:
                    # No validator exists yet for this target in the model.
                    self._validators[model][target] = (validator,)
            else:
                self._validators[model] = {target: (validator,)}

            return validator

        return decorator

    @classmethod
    def get_validators(
        self, model: Type["ValidatableModel"]
    ) -> Dict[ValidationTarget, Tuple[Callable, ...]]:
        return self._validators.get(model, {})


class ValidatableModel(BaseModel):
    """Base class for all models that should support dynamic validators"""

    @model_validator(mode="after")
    def run_dynamic_validators(self) -> "ValidatableModel":
        current_value = self
        # Run model-level validators
        for key, validators in ValidatorRegistry.get_validators(self.__class__).items():
            match key:
                case Model():
                    for validator in validators:
                        current_value = validator(current_value)
                case Field(field_name=f_name):
                    for validator in validators:
                        current_field_value = getattr(self, f_name)
                        setattr(self, f_name, validator(current_field_value))

        return current_value
