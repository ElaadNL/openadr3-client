from collections.abc import Callable
from typing import ClassVar, final

from pydantic import model_validator

from openadr3_client.common._dict_helper import union_with
from openadr3_client.models._base_model import BaseModel


class Model:
    """Represents a model level validation target."""


class Field:
    """Represents a field level validation target."""

    field_name: str

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name


ValidationTarget = Model | Field

DefaultTarget = Model()


# TODO(NICBUR): This is not the nicest way to do this, but it's good enough for now. # noqa: FIX002
# Will look into a better solution as part of v1.1
# https://github.com/ElaadNL/openadr3-client/issues/7
@final
class ValidatorRegistry:
    """
    Registry which stores dynamic pydantic validators associated with a specific model.

    Validators can be dynamically registered by external packages to extend the validation(s) performed
    on the domain objects of this library. By default, this library will only validate according to the
    OpenADR 3 specification.
    """

    _validators: ClassVar[dict[type["ValidatableModel"], dict[ValidationTarget, tuple[Callable, ...]]]] = {}

    @classmethod
    def register(
        cls,
        model: type["ValidatableModel"],
        target: ValidationTarget = DefaultTarget,
    ) -> Callable:
        """Decorator to register validators for specific models and fields."""

        def decorator(validator: Callable) -> Callable:
            if target_dict := cls._validators.get(model):
                if existing_validators := target_dict.get(target):
                    # Target already exists in the validators for the model, simply
                    # update the validators.
                    new_validators = (validator, *existing_validators)
                    cls._validators[model][target] = new_validators
                else:
                    # No validator exists yet for this target in the model.
                    cls._validators[model][target] = (validator,)
            else:
                cls._validators[model] = {target: (validator,)}

            return validator

        return decorator

    @classmethod
    def get_validators(cls, model: type["ValidatableModel"]) -> dict[ValidationTarget, tuple[Callable, ...]]:
        """
        Get the validators that are relevant for the given model.

        Args:
            model (type[&quot;ValidatableModel&quot;]): The model to fetch validators for.

        Returns:
            dict[ValidationTarget, tuple[Callable, ...]]: The validators to execute on the model.

        """
        # First we retrieve the validators for the specific type.
        validators = cls._validators.get(model, {})

        # Afterwards, we retrieve the validators for the base class(es) of the model.
        for base_cls in model.__mro__:
            base_class_validators = cls._validators.get(base_cls, {})

            validators = union_with(lambda a, b: a + b, validators, base_class_validators)

        return validators


class ValidatableModel(BaseModel):
    """Base class for all models that should support dynamic validators."""

    @model_validator(mode="after")
    def run_dynamic_validators(self) -> "ValidatableModel":
        """Runs registered validators of the validator registry on the model."""
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
