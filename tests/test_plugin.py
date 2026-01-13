# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for the plugin system."""

from typing import TypedDict, Unpack

import pytest
from pydantic import ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from openadr3_client.oadr310.models.ven.ven import NewVenVenRequest, Ven
from openadr3_client.plugin import ValidatorPlugin, ValidatorPluginRegistry


def validate_no_numbers(ven_name: str) -> None:
    """Test model validator that checks for numbers in name."""
    if ven_name and any(char.isdigit() for char in ven_name):
        msg = "Name cannot contain numbers"
        raise ValueError(msg)


def validate_name_length(ven_name: str) -> None:
    """Test field validator that checks field value length."""
    if ven_name and len(ven_name) < 3:
        msg = "Name too short"
        raise ValueError(msg)


def _validate_name_length_model_validator_value_error(ven: Ven) -> None:
    if ven.ven_name and len(ven.ven_name) < 3:
        msg = "Name too short (ValueError)"
        raise ValueError(msg)


def _validate_name_length_model_validator_init_error_details(ven: Ven) -> list[InitErrorDetails] | None:
    if ven.ven_name and len(ven.ven_name) < 3:
        msg = "Name too short (InitErrorDetails)"
        return [
            InitErrorDetails(
                type=PydanticCustomError("value_error", msg),
                loc=("ven_name",),
                input=ven.ven_name,
            )
        ]
    return None


class SamplePlugin(ValidatorPlugin):
    """Test plugin that provides name validation."""

    @staticmethod
    def setup(*_args, **_kwargs) -> "SamplePlugin":
        """Setup the plugin."""
        plugin = SamplePlugin()
        plugin.register_field_validator(Ven, "ven_name", validate_name_length)
        return plugin


class NewVenSamplePlugin(ValidatorPlugin):
    """Test plugin that provides NewVen validation."""

    @staticmethod
    def setup(*_args, **_kwargs) -> "NewVenSamplePlugin":
        """Setup the plugin."""
        plugin = NewVenSamplePlugin()

        def validate_new_ven_name_length(ven_name: str) -> None:
            """Test field validator that checks field value length."""
            if ven_name and len(ven_name) < 3:
                msg = "Name too short"
                raise ValueError(msg)

        plugin.register_field_validator(NewVenVenRequest, "ven_name", validate_new_ven_name_length)
        return plugin


class VenValidatorPlugin(ValidatorPlugin):
    """Test plugin for Ven validation."""

    @staticmethod
    def setup(*_args, **_kwargs) -> "VenValidatorPlugin":
        """Setup the plugin."""
        plugin = VenValidatorPlugin()
        plugin.register_field_validator(Ven, "ven_name", validate_no_numbers)
        return plugin


class MultiValidatorPlugin(ValidatorPlugin):
    """Test plugin that provides multiple validators."""

    @staticmethod
    def setup(*_args, **_kwargs) -> "MultiValidatorPlugin":
        """Setup the plugin."""
        plugin = MultiValidatorPlugin()
        plugin.register_field_validator(Ven, "ven_name", validate_name_length)
        plugin.register_field_validator(Ven, "ven_name", validate_no_numbers)
        return plugin


class SamplePluginKwargs(TypedDict):
    """Type for SamplePluginWithSetupKwargs setup kwargs."""

    version: str


class SamplePluginWithSetupKwargs(ValidatorPlugin):
    """Test plugin with setup kwargs."""

    version: str

    def __init__(self, version: str) -> None:
        """Initialize with version."""
        super().__init__()
        self.version = version

    @staticmethod
    def setup(**kwargs: Unpack[SamplePluginKwargs]) -> "SamplePluginWithSetupKwargs":
        """Setup the plugin with kwargs."""
        version = kwargs.get("version")  # Default value if not provided
        if not isinstance(version, str):
            error_msg = "version must be a string"
            raise TypeError(error_msg)
        return SamplePluginWithSetupKwargs(version)


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
        NewVenVenRequest(ven_name="Hi")
    assert "Name too short" in str(exc_info.value)


def test_validator_runs_for_class():
    """Test that class with plugins performs validation for the same class instead of a parent class."""
    plugin = NewVenSamplePlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that validation fails for short names
    with pytest.raises(ValidationError) as exc_info:
        NewVenVenRequest(ven_name="Hi")
    assert "Name too short" in str(exc_info.value)


def test_base_class_validator_runs_for_subclass():
    """Test that base class validator runs for subclass."""
    plugin = VenValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test both validators run
    with pytest.raises(ValidationError) as exc_info:
        NewVenVenRequest(ven_name="Test123")
    assert "Name cannot contain numbers" in str(exc_info.value)


def test_registry_with_plugins_allows_valid_data():
    """Test that class with plugins allows valid data."""
    plugin = SamplePlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that validation passes for valid names
    valid_instance = NewVenVenRequest(ven_name="Valid Name")
    assert valid_instance.name == "Valid Name"


def test_original_class_without_plugins():
    """Test that original class works without any plugins."""
    original = NewVenVenRequest(ven_name="Hi")
    assert original.name == "Hi"


def test_multiple_validators_in_plugin():
    """Test that multiple validators in a plugin all run."""
    plugin = MultiValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test both validators run
    with pytest.raises(ValidationError) as exc_info:
        NewVenVenRequest(ven_name="a1")
    error_str = str(exc_info.value)
    assert "Name too short" in error_str
    assert "Name cannot contain numbers" in error_str

    # Valid data should pass
    valid_instance = NewVenVenRequest(ven_name="ValidName")
    assert valid_instance.name == "ValidName"


def test_plugin_with_setup_kwargs():
    """Test that plugin with setup kwargs works."""
    plugin = SamplePluginWithSetupKwargs.setup(version="1.0.0")
    assert plugin.version == "1.0.0"


def test_field_validator():
    """Test field-level validators."""

    class FieldValidatorPlugin(ValidatorPlugin):
        @staticmethod
        def setup() -> "FieldValidatorPlugin":
            plugin = FieldValidatorPlugin()
            plugin.register_field_validator(Ven, "ven_name", validate_name_length)
            return plugin

    plugin = FieldValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that field validation fails
    with pytest.raises(ValidationError) as exc_info:
        NewVenVenRequest(ven_name="ab")
    assert "1 validation error for NewVen" in str(exc_info.value)
    assert "Name too short" in str(exc_info.value)
    # Test that field validation passes
    valid_instance = NewVenVenRequest(ven_name="ven_valid")
    assert valid_instance.name == "ven_valid"


def test_model_validator_using_value_error():
    """Test model validator using ValueError."""

    class ModelValidatorPlugin(ValidatorPlugin):
        @staticmethod
        def setup() -> "ModelValidatorPlugin":
            plugin = ModelValidatorPlugin()
            plugin.register_model_validator(Ven, _validate_name_length_model_validator_value_error)
            return plugin

    plugin = ModelValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that model validation fails
    with pytest.raises(ValidationError) as exc_info:
        NewVenVenRequest(ven_name="a")
    assert "Name too short" in str(exc_info.value)


def test_model_validator_using_init_error_details():
    """Test model validator using InitErrorDetails."""

    class ModelValidatorPlugin(ValidatorPlugin):
        @staticmethod
        def setup() -> "ModelValidatorPlugin":
            plugin = ModelValidatorPlugin()
            plugin.register_model_validator(Ven, _validate_name_length_model_validator_init_error_details)
            return plugin

    plugin = ModelValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that model validation fails
    with pytest.raises(ValidationError) as exc_info:
        NewVenVenRequest(ven_name="a")
    assert "Name too short" in str(exc_info.value)


def test_mixed_validators():
    """Test mixing model and field validators."""

    class MixedValidatorPlugin(ValidatorPlugin):
        @staticmethod
        def setup() -> "MixedValidatorPlugin":
            plugin = MixedValidatorPlugin()
            # Model validator (using ValueError)
            plugin.register_model_validator(Ven, _validate_name_length_model_validator_value_error)
            # Model validator (using InitErrorDetails)
            plugin.register_model_validator(Ven, _validate_name_length_model_validator_init_error_details)
            # Field validator
            plugin.register_field_validator(Ven, "ven_name", validate_name_length)
            return plugin

    plugin = MixedValidatorPlugin.setup()
    ValidatorPluginRegistry.register_plugin(plugin)

    # Test that both validators fail
    with pytest.raises(ValidationError) as exc_info:
        NewVenVenRequest(ven_name="a")
    error_str = str(exc_info.value)
    assert "3 validation errors for NewVen" in error_str
    assert "Name too short" in error_str
    assert "Name too short (ValueError)" in error_str
    assert "Name too short (InitErrorDetails)" in error_str

    # Test that valid data passes all validators
    valid_instance = NewVenVenRequest(ven_name="ven_validname")
    assert valid_instance.name == "ven_validname"
