import pandas as pd
import pytest

from openadr3_client.oadr301.conversion.input.events.pandas import PandasEventIntervalConverter
from openadr3_client.oadr301.conversion.output.events.pandas import (
    PandasEventIntervalConverter as PandasEventIntervalConverterOutput,
)


def get_original_inputs() -> list[pd.DataFrame]:
    """Returns a list of dataframe inputs for the test."""
    return [
        pd.DataFrame(
            {
                "id": 0,
                "start": pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                "duration": pd.Timedelta(hours=1),
                "randomize_start": pd.Timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [[1.0, 2.0]],
            }
        ).set_index("id"),
        pd.DataFrame(
            {
                "id": [0, 1],
                "start": [
                    pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                    pd.Timestamp("2024-01-01 00:00:00.000Z").as_unit("ns"),
                ],
                "duration": [pd.Timedelta(hours=1), pd.Timedelta(minutes=5)],
                "randomize_start": [
                    pd.Timedelta(minutes=5),
                    pd.Timedelta(minutes=15),
                ],
                "type": ["SIMPLE", "PRICE"],
                "values": [[1.0, 2.0], ["test", "test2"]],
            }
        ).set_index("id"),
        pd.DataFrame(
            {
                "id": [0],
                "start": [
                    pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns"),
                ],
                "duration": [pd.Timedelta(minutes=5)],
                "type": [
                    "SIMPLE",
                ],
                "values": [
                    [1.0, 2.0],
                ],
                "randomize_start": pd.Series([pd.Timedelta("NaT")], dtype="timedelta64[ns]"),
            }
        ).set_index("id"),
        pd.DataFrame(
            {
                "id": [0],
                "type": [
                    "SIMPLE",
                ],
                "values": [
                    [1.0, 2.0],
                ],
                "start": pd.Series([pd.Timedelta("NaT")], dtype="datetime64[ns, UTC]"),
                "duration": pd.Series([pd.Timedelta("NaT")], dtype="timedelta64[ns]"),
                "randomize_start": pd.Series([pd.Timedelta("NaT")], dtype="timedelta64[ns]"),
            }
        ).set_index("id"),
    ]


@pytest.mark.parametrize("df_input", get_original_inputs())
def test_conversion_iterable(df_input: pd.DataFrame) -> None:
    """Tests the conversion of pandas dataframes to event intervals."""
    input_converter = PandasEventIntervalConverter()
    output_converter = PandasEventIntervalConverterOutput()

    input_intervals = input_converter.convert(df_input)
    output_intervals = output_converter.convert(input_intervals)

    # Sort columns alphabetically (requirement for equality check)
    input_df_sorted = df_input[sorted(df_input.columns)]
    output_df_sorted = output_intervals[sorted(output_intervals.columns)]

    assert input_df_sorted.equals(output_df_sorted)
