"""Tests for the plugin system."""

from typing import TypedDict, Unpack

import pytest
from pydantic import ValidationError

from openadr3_client.models.model import ValidatableModel
from openadr3_client.plugin import Validator, ValidatorPlugin, ValidatorPluginRegistry


class SampleModel(ValidatableModel):
    """Test model for plugin validation."""

    name: str


class NameValidator(Validator):
    """Test validator that checks name length."""

    def validate(self, model: SampleModel) -> None:
        """Validate the model."""
        if len(model.name) < 3:
            msg = "Name too short"
            raise ValueError(msg)


class SamplePlugin(ValidatorPlugin):
    """Test plugin that provides name validation."""

    def __init__(self) -> None:
        super().__init__("test_plugin")

    @staticmethod
    def setup(*_args, **_kwargs) -> "SamplePlugin":
        """Setup the plugin."""
        plugin = SamplePlugin()
        validator = NameValidator(model=SampleModel, validator_name="name_length_validator")
        plugin.register_validator(validator)
        return plugin


@pytest.fixture(autouse=True)
def clear_plugins():
    """Clear plugins after each test."""
    yield
    ValidatorPluginRegistry.clear_plugins()


def test_registry_with_plugins_validates():
    """Test that class with plugins performs validation."""
    plugin = SamplePlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that validation fails for short names
    with pytest.raises(ValidationError) as exc_info:
        SampleModel(name="Hi")
    assert (
        "Validation error from plugin validator test_plugin.SampleModel.name_length_validator: Name too short"
        in str(exc_info.value)
    )


def test_registry_with_plugins_allows_valid_data():
    """Test that class with plugins allows valid data."""
    plugin = SamplePlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that validation passes for valid names
    valid_instance = SampleModel(name="Valid Name")
    assert valid_instance.name == "Valid Name"


def test_original_class_without_plugins():
    """Test that original class works without any plugins."""
    original = SampleModel(name="Hi")
    assert original.name == "Hi"


def test_multiple_validators_in_plugin():
    """Test that multiple validators in a plugin all run."""

    class NoNumbersValidator(Validator):
        def validate(self, model: SampleModel) -> None:
            if any(char.isdigit() for char in model.name):
                msg = "Name cannot contain numbers"
                raise ValueError(msg)

    class MultiValidatorPlugin(ValidatorPlugin):
        def __init__(self) -> None:
            super().__init__("multi_validator")

        @staticmethod
        def setup(*_args, **_kwargs) -> "MultiValidatorPlugin":
            plugin = MultiValidatorPlugin()

            name_validator = NameValidator(model=SampleModel, validator_name="name_validator")
            no_numbers_validator = NoNumbersValidator(model=SampleModel, validator_name="no_numbers_validator")

            plugin.register_validator(name_validator).register_validator(no_numbers_validator)
            return plugin

    plugin = MultiValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test both validators run
    with pytest.raises(ValidationError) as exc_info:
        SampleModel(name="Hi")
    assert "Name too short" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SampleModel(name="Test123")
    assert "Name cannot contain numbers" in str(exc_info.value)

    # Valid data should pass
    valid_instance = SampleModel(name="ValidName")
    assert valid_instance.name == "ValidName"


def test_plugin_with_setup_kwargs():
    """Test that plugin with setup kwargs works."""

    class SamplePluginKwargs(TypedDict):
        version: str

    class SamplePluginWithSetupKwargs(ValidatorPlugin):
        version: str

        def __init__(self, version: str) -> None:
            super().__init__("test_plugin_with_setup_kwargs")
            self.version = version

        @staticmethod
        def setup(**kwargs: Unpack[SamplePluginKwargs]) -> "SamplePluginWithSetupKwargs":
            version = kwargs.get("version")  # Default value if not provided
            if not isinstance(version, str):
                error_msg = "version must be a string"
                raise TypeError(error_msg)
            return SamplePluginWithSetupKwargs(version)

    plugin = SamplePluginWithSetupKwargs.setup(version="1.0.0")
    assert plugin.version == "1.0.0"
