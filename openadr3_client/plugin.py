from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, ClassVar, Self, TypeVar, cast, final

from pydantic_core import InitErrorDetails, PydanticCustomError

T = TypeVar("T")

# Type definitions for validators
ModelValidatorFunc = Callable[[T], list[InitErrorDetails] | None]
FieldValidatorFunc = Callable[[T], None]  # Field validators take only field_value and raise ValueError on failure
ValidatorFunc = ModelValidatorFunc[T] | FieldValidatorFunc


class ValidatorInfo:
    """Metadata about a registered validator function."""

    def __init__(
        self,
        func: ValidatorFunc[T],
        model: type[T],
        plugin_name: str,
        field_name: str | None = None,
    ) -> None:
        """
        Initialize validator info.

        Args:
            func: The validator function
            model: The model type this validator applies to
            field_name: Optional field name for field-level validators
            plugin_name: The name of the plugin this validator belongs to

        """
        self.func = func
        self.model = model
        self.field_name = field_name
        self.plugin_name = plugin_name

    def validate(self, value: T) -> list[InitErrorDetails] | None:
        """Run the validator function."""
        # If no field name is defined, the validator must be a model validator
        if self.field_name is None:
            try:
                # Cast to ModelValidatorFunc so mypy knows this is a model validator
                model_func = cast("ModelValidatorFunc[T]", self.func)
                errors = model_func(value)
            # Option 1: return a single error
            except ValueError as e:
                return [
                    InitErrorDetails(
                        type=PydanticCustomError("value_error", str(e)),
                        input=value,
                        ctx={"plugin_name": self.plugin_name},
                    )
                ]
            # Option 2: return a list of errors
            if errors:
                # Create new InitErrorDetails with plugin_name in ctx
                modified_errors = []
                for error in errors:
                    error["ctx"] = {**error.get("ctx", {}), "plugin_name": self.plugin_name}
                    modified_errors.append(error)
                return modified_errors
            return None

        # If a field name is defined, the validator must be a field validator
        field_name = self.field_name
        field_value = getattr(value, field_name, None)
        try:
            # Cast to FieldValidatorFunc so mypy knows this is a field validator
            field_func = cast("FieldValidatorFunc", self.func)
            field_func(field_value)
        except ValueError as e:
            return [
                InitErrorDetails(
                    type=PydanticCustomError("value_error", str(e)),
                    loc=(field_name,),
                    input=field_value,
                    ctx={"plugin_name": self.plugin_name},
                )
            ]
        else:
            return None


class ValidatorPlugin(ABC):
    """
    Plugin for the OpenADR 3 client.

    This class serves as a base for creating validation plugins that can extend
    the validation capabilities of OpenADR models. Each plugin can contain multiple
    validators that operate on specific models or fields.

    Example:
        Creating a custom validation plugin with function-based validators:

        >>> from typing import Any
        >>> from pydantic_core import InitErrorDetails, PydanticCustomError
        >>> from openadr3_client.models.event.event import Event
        >>> from openadr3_client.plugin import ValidatorPlugin

        >>> def validate_event_name_length(event: Event) -> list[InitErrorDetails] | None:
        ...     '''Model-level validator for event name length.'''
        ...     if event.event_name and len(event.event_name) < 3:
        ...         return [InitErrorDetails(
        ...             type=PydanticCustomError("value_error", "Event name must be at least 3 characters"),
        ...             loc=("event_name",),
        ...             input=event.event_name,
        ...         )]
        ...     return None

        >>> def validate_event_intervals_duration(event: Event) -> None:
        ...     '''Model-level validator that throws ValueError for invalid interval durations.'''
        ...     from datetime import timedelta
        ...     required_duration = timedelta(hours=1)  # PT1H
        ...     for interval in event.intervals:
        ...         if interval.interval_period and interval.interval_period.duration != required_duration:
        ...             raise ValueError("All intervals must have duration of 1 hour for this profile")

        >>> def validate_event_id_format(field_value: str) -> None:
        ...     '''Field-level validator for event ID format.'''
        ...     if field_value and not field_value.startswith("event_"):
        ...         raise ValueError("Event ID must start with 'event_'")

        >>> class ProfileValidationPlugin(ValidatorPlugin):
        ...     def __init__(self, profile_version: str) -> None:
        ...         super().__init__()
        ...         self.profile_version = profile_version
        ...
        ...     @staticmethod
        ...     def setup(*args: Any, **kwargs: Any) -> "ProfileValidationPlugin":
        ...         profile_version = kwargs.get("profile_version", "1.0")
        ...         plugin = ProfileValidationPlugin(profile_version=profile_version)
        ...         if profile_version.startswith("1."):
        ...             plugin.register_model_validator(Event, validate_event_name_length)
        ...         elif profile_version.startswith("2."):
        ...             plugin.register_model_validator(Event, validate_event_intervals_duration)
        ...             plugin.register_model_validator(Event, validate_event_name_length)
        ...         plugin.register_field_validator(Event, "id", validate_event_id_format)
        ...         return plugin

        Usage examples:

        >>> legacy_plugin = ProfileValidationPlugin.setup(profile_version="1.2")
        >>> legacy_plugin.profile_version
        '1.2'
        >>> len(legacy_plugin.validators)
        2

        >>> modern_plugin = ProfileValidationPlugin.setup(profile_version="2.1")
        >>> modern_plugin.profile_version
        '2.1'
        >>> len(modern_plugin.validators)
        3

        Testing validation with the plugin:

        >>> from openadr3_client.plugin import ValidatorPluginRegistry
        >>> from openadr3_client.models.event.event import NewEvent, ExistingEvent
        >>> from openadr3_client.models.common.interval import Interval
        >>> from openadr3_client.models.common.interval_period import IntervalPeriod
        >>> from openadr3_client.models.event.event_payload import EventPayload
        >>> from datetime import datetime, timezone, timedelta

        >>> # Register the legacy plugin first
        >>> ValidatorPluginRegistry.clear_plugins()  # Clear any existing plugins
        >>> ValidatorPluginRegistry.register_plugin(legacy_plugin)
        <class 'openadr3_client.plugin.ValidatorPluginRegistry'>

        >>> # Create a valid NewEvent (note: NewEvent doesn't have 'id' field, so field validator won't run)
        >>> valid_event = NewEvent(
        ...     program_id="test_program",
        ...     event_name="Valid Event Name",  # Long enough (>= 3 chars)
        ...     intervals=[Interval(
        ...         id=1,
        ...         interval_period=IntervalPeriod(
        ...             start=datetime.now(timezone.utc),
        ...             duration=timedelta(hours=1)
        ...         ),
        ...         payloads=[EventPayload(type="SIMPLE", values=[1.0])]
        ...     )]
        ... )
        >>> valid_event.event_name
        'Valid Event Name'

        >>> # Validation error for short event name (model validator)
        >>> try:
        ...     NewEvent(
        ...         program_id="test_program",
        ...         event_name="Hi",  # Too short (< 3 chars)
        ...         intervals=[Interval(
        ...             id=1,
        ...             interval_period=IntervalPeriod(
        ...                 start=datetime.now(timezone.utc),
        ...                 duration=timedelta(hours=1)
        ...             ),
        ...             payloads=[EventPayload(type="SIMPLE", values=[1.0])]
        ...         )]
        ...     )
        ... except Exception as e:
        ...     print("Model validation error:", "Event name must be at least 3 characters" in str(e))
        Model validation error: True

        >>> # Field validation with ExistingEvent (which has 'id' field)
        >>> try:
        ...     ExistingEvent(
        ...         program_id="test_program",
        ...         event_name="Valid Name",
        ...         id="invalid_123",  # Doesn't start with "event_"
        ...         created_date_time=datetime.now(timezone.utc),
        ...         modification_date_time=datetime.now(timezone.utc),
        ...         intervals=[Interval(
        ...             id=1,
        ...             interval_period=IntervalPeriod(
        ...                 start=datetime.now(timezone.utc),
        ...                 duration=timedelta(hours=1)
        ...             ),
        ...             payloads=[EventPayload(type="SIMPLE", values=[1.0])]
        ...         )]
        ...     )
        ... except Exception as e:
        ...     print("Field validation error:", "Event ID must start with 'event_'" in str(e))
        Field validation error: True

        >>> # ValueError model validator with modern plugin
        >>> ValidatorPluginRegistry.clear_plugins()
        >>> ValidatorPluginRegistry.register_plugin(modern_plugin)
        <class 'openadr3_client.plugin.ValidatorPluginRegistry'>

        >>> # Validation error for wrong interval duration (ValueError model validator)
        >>> try:
        ...     NewEvent(
        ...         program_id="test_program",
        ...         event_name="Valid Name",
        ...         intervals=[Interval(
        ...             id=1,
        ...             interval_period=IntervalPeriod(
        ...                 start=datetime.now(timezone.utc),
        ...                 duration=timedelta(minutes=30)  # Wrong duration - should be 1 hour
        ...             ),
        ...             payloads=[EventPayload(type="SIMPLE", values=[1.0])]
        ...         )]
        ...     )
        ... except Exception as e:
        ...     print("ValueError model validation:", "All intervals must have duration of 1 hour" in str(e))
        ValueError model validation: True

    """

    validators: list[ValidatorInfo]

    def __init__(self) -> None:
        """Initialize the plugin."""
        self.validators = []

    @staticmethod
    @abstractmethod
    def setup(*args: Any, **kwargs: Any) -> "ValidatorPlugin":  # noqa: ANN401
        """Set up the plugin. Returns an instance of the plugin."""

    def get_model_validators(self, model: type[T]) -> tuple[ValidatorInfo, ...]:
        """Get all validators for a specific model."""
        return tuple(validator for validator in self.validators if validator.model in model.__mro__)

    def register_model_validator(
        self,
        model: type[T],
        validator_func: ModelValidatorFunc[T],
    ) -> Self:
        """
        Register a model-level validator function.

        Args:
            model: The model type this validator applies to
            validator_func: Function that takes a model instance and returns validation errors

        Returns:
            Self for method chaining

        """
        validator_info = ValidatorInfo(
            func=validator_func,
            model=model,
            plugin_name=self.__class__.__name__,
            field_name=None,
        )
        self.validators.append(validator_info)
        return self

    def register_field_validator(
        self,
        model: type[T],
        field_name: str,
        validator_func: FieldValidatorFunc,
    ) -> Self:
        """
        Register a field-level validator function.

        Args:
            model: The model type this validator applies to
            field_name: The field name to validate
            validator_func: Function that takes (field_value) and raises ValueError
                on validation failure

        Returns:
            Self for method chaining

        """
        validator_info = ValidatorInfo(
            func=validator_func,
            model=model,
            plugin_name=self.__class__.__name__,
            field_name=field_name,
        )
        self.validators.append(validator_info)
        return self

    def register_validator(self, validator_info: ValidatorInfo) -> Self:
        """
        Register a validator info object directly.

        Args:
            validator_info: Pre-configured validator info

        Returns:
            Self for method chaining

        """
        # Set plugin name if not already set
        if not validator_info.plugin_name:
            validator_info.plugin_name = self.__class__.__name__
        self.validators.append(validator_info)
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
            MyFirstPlugin.setup(profile_version="1.2")
        ).register_plugin(
            MySecondPlugin.setup(profile_version="2.1")
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
    def get_model_validators(cls, model: type[T]) -> tuple[ValidatorInfo, ...]:
        """Get all validators for a specific model. Used by the ValidatableModel class."""
        validators: list[ValidatorInfo] = []
        for plugin in cls._plugins:
            validators.extend(plugin.get_model_validators(model))
        return tuple(validators)
