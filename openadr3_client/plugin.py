from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generic, Self, TypeVar, final

T = TypeVar("T")


class Validator(ABC, Generic[T]):
    """Validator for a specific model."""

    model: type[T]
    validator_name: str

    def __init__(
        self,
        model: type[T],
        validator_name: str,
    ) -> None:
        """Initialize the validator."""
        self.model = model
        self.validator_name = validator_name

    @abstractmethod
    def validate(self, value: T) -> None:
        """
        Validate the value (either a model instance or field value).

        Args:
            value: The value to validate.

        Returns:
            None

        Raises:
            ValidationError: If the value is not valid.

        """

    def register_with_plugin(self, plugin: "ValidatorPlugin") -> None:
        """Register the validator with the plugin."""
        self.plugin = plugin

    def get_validator_id(self) -> str:
        """Get the validator id."""
        return f"{self.plugin.name}.{self.model.__name__}.{self.validator_name}"


class ValidatorPlugin(ABC):
    """
    Plugin for the OpenADR 3 client.

    This class serves as a base for creating validation plugins that can extend
    the validation capabilities of OpenADR models. Each plugin can contain multiple
    validators that operate on specific models.

    Example:
        Creating a custom validation plugin:

        ```python
        from openadr3_client.plugin import ValidatorPlugin, Validator
        from openadr3_client.models.event.event import Event

        class LegacyEventValidator(Validator[Event]):
            def validate(self, model: Event) -> None:
                # Legacy validation - simple name check
                if model.event_name and len(model.event_name) < 3:
                    raise ValueError("Event name must be at least 3 characters")

        class ModernEventValidator(Validator[Event]):
            def validate(self, model: Event) -> None:
                # Modern validation - stricter rules
                if not model.event_name:
                    raise ValueError("Event name is required in v2.0+")
                if len(model.event_name) < 5:
                    raise ValueError("Event name must be at least 5 characters in v2.0+")

        class ProfileValidationPlugin(ValidatorPlugin):
            def __init__(self, profile_version: str) -> None:
                super().__init__()
                self.profile_version = profile_version

            @property
            def name(self) -> str:
                return f"profile_validator_{self.profile_version}"

            @staticmethod
            def setup(*args: Any, **kwargs: Any) -> "ProfileValidationPlugin":
                # Extract the profile version to validate against
                profile_version = kwargs.get("profile_version", "1.0")

                # Create the plugin instance
                plugin = ProfileValidationPlugin(profile_version=profile_version)

                # Add different validators based on the profile version
                if profile_version.startswith("1."):
                    # Legacy profile - basic validation
                    validator = LegacyEventValidator(
                        plugin=plugin,
                        model=Event,
                        validator_name="legacy_validator"
                    )
                    plugin.register_validator(validator)
                elif profile_version.startswith("2."):
                    # Modern profile - stricter validation
                    validator = ModernEventValidator(
                        plugin=plugin,
                        model=Event,
                        validator_name="modern_validator"
                    )
                    plugin.register_validator(validator)
                else:
                    raise ValueError(f"Unsupported profile version: {profile_version}")

                return plugin

        # Usage for different profile versions:

        # Legacy profile validation
        legacy_plugin = ProfileValidationPlugin.setup(profile_version="1.2")
        print(f"Legacy plugin: {legacy_plugin.name}")  # profile_validator_1.2

        # Modern profile validation
        modern_plugin = ProfileValidationPlugin.setup(profile_version="2.1")
        print(f"Modern plugin: {modern_plugin.name}")  # profile_validator_2.1
        ```

    """

    validators: list[Validator]
    name: str

    def __init__(self, name: str) -> None:
        """Initialize the plugin."""
        self.name = name
        self.validators = []

    @staticmethod
    @abstractmethod
    def setup(*args: Any, **kwargs: Any) -> "ValidatorPlugin":  # noqa: ANN401
        """Set up the plugin. Returns an instance of the plugin."""

    def get_model_validators(self, model: type[T]) -> tuple[Validator[T], ...]:
        """Get all validators for a specific model."""
        return tuple(validator for validator in self.validators if validator.model in model.__mro__)

    def register_validator(self, validator: Validator) -> Self:
        """Add a validator to this plugin."""
        if not isinstance(validator, Validator):
            msg = f"All validators must be Validator instances, got {type(validator)}"
            raise TypeError(msg)
        validator.register_with_plugin(self)
        self.validators.append(validator)
        return self


@final
class ValidatorPluginRegistry:
    """
    Global registry which stores Validator plugins.

    Validators can be dynamically registered by external packages to extend the validation(s) performed
    on the domain objects of this library. By default, this library will only validate according to the
    OpenADR 3 specification.

    Example:
        ```python
        from openadr3_client.plugin import ValidatorPluginRegistry, ValidatorPlugin
        from openadr3_client.models.event.event import Event

        ValidatorPluginRegistry.register_plugin(
            MyFirstPlugin(
                profile_version="1.2"
            )
        ).register_plugin(
            MySecondPlugin(
                profile_version="2.1"
            )
        )
        ```

    """

    _plugins: ClassVar[list[ValidatorPlugin]] = []

    @classmethod
    def register_plugin(cls, plugin: ValidatorPlugin) -> type[Self]:
        """
        Register a plugin.

        Args:
            plugin (ValidatorPlugin): The plugin to register.

        Returns:
            type[Self]: The registry instance.

        """
        if not isinstance(plugin, ValidatorPlugin):
            msg = f"All plugins must be ValidatorPlugin instances, got {type(plugin)}"
            raise TypeError(msg)
        cls._plugins.append(plugin)

        return cls

    @classmethod
    def clear_plugins(cls) -> None:
        """Clear all plugins from the registry."""
        cls._plugins = []

    @classmethod
    def get_model_validators(cls, model: type[T]) -> tuple[Validator[T], ...]:
        """Get all validators for a specific model. Used by the ValidatableModel class."""
        validators: list[Validator[T]] = []
        for plugin in cls._plugins:
            validators.extend(plugin.get_model_validators(model))
        return tuple(validators)
