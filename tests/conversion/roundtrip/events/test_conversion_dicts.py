from datetime import UTC, datetime, timedelta

import pytest
from openadr3_client.conversion.common.dict import EventIntervalDictInput
from openadr3_client.conversion.input.events.dict import DictEventIntervalConverter
from openadr3_client.conversion.output.events.dict import DictEventIntervalConverter as DictEventIntervalConverterOutput

def get_original_inputs() -> list[list[EventIntervalDictInput]]:
    """Returns a list of dict inputs for the test."""
    return [
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(hours=1),
                "randomize_start": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            }
        ],
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(hours=1),
                "randomize_start": timedelta(minutes=5),
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            },
            {
                "start": datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(minutes=5),
                "randomize_start": timedelta(minutes=15),
                "type": "PRICE",
                "values": ["test", "test2"],
            },
        ],
        [
            {
                "start": datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
                "duration": timedelta(minutes=5),
                "randomize_start": None,
                "type": "SIMPLE",
                "values": [1.0, 2.0],
            }
        ],
        [
            {
                "type": "SIMPLE",
                "values": [1.0, 2.0],
                "start": None,
                "duration": None,
                "randomize_start": None,
            }
        ],
    ]

@pytest.mark.parametrize("input", get_original_inputs())
def test_conversion_iterable(
    input: list[EventIntervalDictInput]
) -> None:
    """Tests the conversion of pandas dataframes to event intervals."""
    input_converter = DictEventIntervalConverter()
    output_converter = DictEventIntervalConverterOutput()

    input_intervals = input_converter.convert(input)
    output_intervals = output_converter.convert(input_intervals)

    assert input == output_intervals
