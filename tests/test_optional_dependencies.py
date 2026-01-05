"""Tests for optional dependency functionality."""

import importlib
import sys
from unittest.mock import patch

import pytest

from openadr3_client._conversion.input._base_converter import OK


def test_main_package_imports_without_pandas() -> None:
    """Test that the main package can be imported without pandas installed."""
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
