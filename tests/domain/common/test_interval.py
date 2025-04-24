import pytest
from pydantic import ValidationError

from openadr3_client.domain.common.interval import Interval


def test_interval_no_payloads() -> None:
    """Test that verifies that an interval with no payload raises an error."""
    with pytest.raises(
        ValidationError,
        match="interval payload must contain at least one payload",
    ):
        _ = Interval(id=0, interval_period=None, payloads=())
