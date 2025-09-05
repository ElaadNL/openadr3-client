"""Tests for the plugin system."""

from typing import TypedDict, Unpack

import pytest
from pydantic import ValidationError

from openadr3_client.models.ven.ven import NewVen, Ven
from openadr3_client.plugin import Validator, ValidatorPlugin, ValidatorPluginRegistry


class NameValidator(Validator):
    """Test validator that checks name length."""

    @property
    def model(self) -> type[Ven]:
        """The model type this validator validates."""
        return Ven

    def validate(self, model: Ven) -> None:
        """Validate the model."""
        if len(model.ven_name) < 3:
            msg = "Name too short"
            raise ValueError(msg)


class SamplePlugin(ValidatorPlugin):
    """Test plugin that provides name validation."""

    @staticmethod
    def setup(*_args, **_kwargs) -> "SamplePlugin":
        """Setup the plugin."""
        plugin = SamplePlugin()
        validator = NameValidator()
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
        NewVen(ven_name="Hi")
    assert "Validation error from plugin validator SamplePlugin.Ven.NameValidator: Name too short" in str(
        exc_info.value
    )


def test_registry_with_plugins_validates_new_ven():
    """Test that class with plugins performs validation for the same class instead of a parent class."""

    class NewVenNameValidator(Validator):
        """Test validator that checks name length."""

        @property
        def model(self) -> type[NewVen]:
            """The model type this validator validates."""
            return NewVen

        def validate(self, model: NewVen) -> None:
            """Validate the model."""
            if len(model.ven_name) < 3:
                msg = "Name too short"
                raise ValueError(msg)

    class NewVenSamplePlugin(ValidatorPlugin):
        """Test plugin that provides name validation."""

        @staticmethod
        def setup(*_args, **_kwargs) -> "NewVenSamplePlugin":
            """Setup the plugin."""
            plugin = NewVenSamplePlugin()
            validator = NewVenNameValidator()
            plugin.register_validator(validator)
            return plugin

    plugin = NewVenSamplePlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that validation fails for short names
    with pytest.raises(ValidationError) as exc_info:
        NewVen(ven_name="Hi")
    assert (
        "Validation error from plugin validator NewVenSamplePlugin.NewVen.NewVenNameValidator: Name too short"
        in str(exc_info.value)
    )


def test_registry_with_plugins_allows_valid_data():
    """Test that class with plugins allows valid data."""
    plugin = SamplePlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that validation passes for valid names
    valid_instance = NewVen(ven_name="Valid Name")
    assert valid_instance.name == "Valid Name"


def test_original_class_without_plugins():
    """Test that original class works without any plugins."""
    original = NewVen(ven_name="Hi")
    assert original.name == "Hi"


def test_multiple_validators_in_plugin():
    """Test that multiple validators in a plugin all run."""

    class NoNumbersValidator(Validator):
        """Test validator that checks name length."""

        @property
        def model(self) -> type[Ven]:
            """The model type this validator validates."""
            return Ven

        def validate(self, model: Ven) -> None:
            if any(char.isdigit() for char in model.ven_name):
                msg = "Name cannot contain numbers"
                raise ValueError(msg)

    class MultiValidatorPlugin(ValidatorPlugin):
        """Test plugin that provides name validation."""

        @staticmethod
        def setup(*_args, **_kwargs) -> "MultiValidatorPlugin":
            plugin = MultiValidatorPlugin()

            name_validator = NameValidator()
            no_numbers_validator = NoNumbersValidator()

            plugin.register_validator(name_validator).register_validator(no_numbers_validator)
            return plugin

    plugin = MultiValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test both validators run
    with pytest.raises(ValidationError) as exc_info:
        NewVen(ven_name="Hi")
    assert "Name too short" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        NewVen(ven_name="Test123")
    assert "Name cannot contain numbers" in str(exc_info.value)

    # Valid data should pass
    valid_instance = NewVen(ven_name="ValidName")
    assert valid_instance.name == "ValidName"


def test_plugin_with_setup_kwargs():
    """Test that plugin with setup kwargs works."""

    class SamplePluginKwargs(TypedDict):
        version: str

    class SamplePluginWithSetupKwargs(ValidatorPlugin):
        version: str

        def __init__(self, version: str) -> None:
            super().__init__()
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
