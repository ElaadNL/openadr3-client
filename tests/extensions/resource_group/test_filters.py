# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

from openadr3_client.extensions.resource_group._client.filters import PaginationFilter, TargetFilter


def test_target_filter_serializes_by_alias() -> None:
    """Test that TargetFilter serializes model fields using their aliases."""
    assert TargetFilter(targets=["a", "b"]).model_dump(by_alias=True, mode="json") == {"targets": ["a", "b"]}


def test_pagination_filter_serializes_by_alias() -> None:
    """Test that PaginationFilter serializes model fields using their aliases."""
    assert PaginationFilter(skip=5, limit=10).model_dump(by_alias=True, mode="json") == {"skip": 5, "limit": 10}
