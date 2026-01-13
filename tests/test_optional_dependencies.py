# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for optional dependency functionality."""

import importlib
import sys
from unittest.mock import patch

import pytest

from openadr3_client._conversion.input._base_converter import OK


def test_main_package_imports_without_optional_dependencies() -> None:
    """Test that the main package can be imported without any optional dependencies installed."""
    # Note: this test is not bulletproof, some submodules might still import pandas.
    try:
        import openadr3_client  # noqa: F401 PLC0415
    except ImportError:
        pytest.fail("Main package should import successfully without pandas")


def test_pandas_classes_import_successfully_with_pandas() -> None:
    """Test that pandas-dependent classes can be imported successfully when pandas is available."""
    # Test importing the classes as a user would do
    try:
        from openadr3_client._conversion.common.dataframe import EventIntervalDataFrameSchema  # noqa: F401 PLC0415
        from openadr3_client.oadr301.conversion.input.events.pandas import (  # noqa: PLC0415
            PandasEventIntervalConverter,  # noqa: F401
        )
        from openadr3_client.oadr301.conversion.output.events.pandas import (  # noqa: PLC0415
            PandasEventIntervalConverter as OutputConverter,  # noqa: F401
        )
    except ImportError as e:
        pytest.fail(f"Pandas classes should import successfully when dependencies are available: {e}")


def test_pandas_modules_have_import_guards() -> None:
    """Test that verifies that pandas-dependent modules raise an ImportError when pandas is not installed."""
    # Mock the import mechanism to simulate pandas not being available

    def mock_import(name: str, *args, **kwargs) -> object:
        if name in ("pandas", "numpy", "pandera"):
            error_msg = f"No module named '{name}'"
            raise ImportError(error_msg)
        # Use the real import for other modules
        return importlib.__import__(name, *args, **kwargs)

    # Remove pandas-related modules from sys.modules to force re-import
    modules_to_remove = [
        "pandas",
        "numpy",
        "pandera",
        "openadr3_client.oadr301.conversion.input.events.pandas",
        "openadr3_client.oadr301.conversion.output.events.pandas",
        "openadr3_client._conversion.common.dataframe",
    ]

    original_modules = {}
    for module in modules_to_remove:
        if module in sys.modules:
            original_modules[module] = sys.modules[module]
            del sys.modules[module]

    try:
        # Use patch to mock the import
        with patch("builtins.__import__", side_effect=mock_import):
            # Test input module
            with pytest.raises(ImportError) as excinfo:
                importlib.import_module("openadr3_client.oadr301.conversion.input.events.pandas")

            assert "DataFrame conversion functionality requires the 'pandas' extra" in str(excinfo.value)

            # Test output module
            with pytest.raises(ImportError) as excinfo:
                importlib.import_module("openadr3_client.oadr301.conversion.output.events.pandas")

            assert "DataFrame conversion functionality requires the 'pandas' extra" in str(excinfo.value)

    finally:
        # Restore the original modules
        for module, original_module in original_modules.items():
            sys.modules[module] = original_module


def test_pandas_functionality_works_when_available() -> None:
    """Test that pandas functionality works correctly when dependencies are available."""
    # Import at function level to test actual functionality
    try:
        import pandas as pd  # noqa: PLC0415

        from openadr3_client.oadr301.conversion.input.events.pandas import PandasEventIntervalConverter  # noqa: PLC0415
    except ImportError:
        pytest.fail("Pandas should be available for this test")

    # Create a simple test DataFrame
    pandas_dataframe = pd.DataFrame(
        {
            "start": [pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns")],
            "duration": [pd.Timedelta(hours=1)],
            "type": ["SIMPLE"],
            "values": [[1.0, 2.0]],
        }
    )

    # Test that the converter can be instantiated and validate the DataFrame
    converter = PandasEventIntervalConverter()
    validation_result = converter.validate_input(pandas_dataframe)

    assert isinstance(validation_result, OK)


def test_mqtt_classes_import_successfully_with_paho_mqtt() -> None:
    """Test that MQTT-dependent classes can be imported successfully when paho-mqtt is available."""
    # Test importing the classes as a user would do
    try:
        from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient  # noqa: F401 PLC0415
    except ImportError as e:
        pytest.fail(f"MQTT classes should import successfully when dependencies are available: {e}")


def test_mqtt_modules_have_import_guards() -> None:
    """Test that verifies that MQTT-dependent modules raise an ImportError when paho-mqtt is not installed."""
    # Mock the import mechanism to simulate paho-mqtt not being available

    def mock_import(name: str, *args, **kwargs) -> object:
        if name in ("paho.mqtt.client", "paho.mqtt.enums", "paho.mqtt", "paho"):
            error_msg = f"No module named '{name}'"
            raise ImportError(error_msg)
        # Use the real import for other modules
        return importlib.__import__(name, *args, **kwargs)

    # Remove paho-mqtt-related modules from sys.modules to force re-import
    modules_to_remove = [
        "paho",
        "paho.mqtt",
        "paho.mqtt.client",
        "paho.mqtt.enums",
        "openadr3_client.oadr310._vtn.mqtt.client",
    ]

    original_modules = {}
    for module in modules_to_remove:
        if module in sys.modules:
            original_modules[module] = sys.modules[module]
            del sys.modules[module]

    try:
        # Use patch to mock the import
        with patch("builtins.__import__", side_effect=mock_import):
            # Test MQTT client module
            with pytest.raises(ImportError) as excinfo:
                importlib.import_module("openadr3_client.oadr310._vtn.mqtt.client")

            assert "Usage of the MQTT client requires the 'mqtt' extra" in str(excinfo.value)

    finally:
        # Restore the original modules
        for module, original_module in original_modules.items():
            sys.modules[module] = original_module


def test_mqtt_functionality_works_when_available() -> None:
    """Test that MQTT functionality works correctly when dependencies are available."""
    # Import at function level to test actual functionality
    try:
        from openadr3_client.oadr310._vtn.mqtt.client import MQTTClient  # noqa: PLC0415
        from openadr3_client.oadr310.models.notifiers.mqtt.mqtt import (  # noqa: PLC0415
            MqttNotifierAuthenticationAnonymous,
            MqttNotifierBindingObject,
        )
    except ImportError:
        pytest.fail("paho-mqtt should be available for this test")

    # Create a simple test MqttNotifierBindingObject
    mqtt_notifier_binding = MqttNotifierBindingObject(
        URIS=["mqtt://localhost:1883"],  # type: ignore[list-item]
        authentication=MqttNotifierAuthenticationAnonymous(),
    )

    # Test that the MQTTClient can be instantiated
    mqtt_client = MQTTClient(mqtt_notifier_binding)

    # Verify that the client is properly initialized
    assert mqtt_client._mqtt_notifier_binding == mqtt_notifier_binding
    assert mqtt_client._oauth_token_manager is None
