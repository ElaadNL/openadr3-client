# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import UTC, datetime, timedelta

import pytest

from openadr3_client._conversion.common.dict import EventIntervalDictInput
from openadr3_client.oadr301.conversion.input.events.dict import DictEventIntervalConverter
from openadr3_client.oadr301.conversion.output.events.dict import DictEventIntervalConverter as DictEventIntervalConverterOutput


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


@pytest.mark.parametrize("dict_input", get_original_inputs())
def test_conversion_iterable(dict_input: list[EventIntervalDictInput]) -> None:
    """Tests the conversion of pandas dataframes to event intervals."""
    input_converter = DictEventIntervalConverter()
    output_converter = DictEventIntervalConverterOutput()

    input_intervals = input_converter.convert(dict_input)
    output_intervals = output_converter.convert(input_intervals)

    assert dict_input == output_intervals
