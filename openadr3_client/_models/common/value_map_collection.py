# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Contains the ValueMap type."""

import warnings
from typing import Any, get_args

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class ValuesMap[Type, Values](tuple):
    """Tuple of ValuesMap objects with a convenience method for key-based lookup."""

    __slots__ = ()

    def get_by_type(self, key: Type) -> Values | None:
        """
        Return the first entry whose type matches key.

        Warns if multiple entries share the same key, as the OpenADR 3 specification
        is ambiguous about whether this is valid. Please open an issue if you have a valid use-case: https://github.com/ElaadNL/openadr3-client/issues
        """
        matches = [item for item in self if item.type == key]  # type: ignore[attr-defined]
        if len(matches) > 1:
            warnings.warn(
                f"Multiple valueMap entries found for key '{key}'. Returning the first match.",
                stacklevel=2,
            )
        return matches[0] if matches else None

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        args = get_args(source_type)
        _min_args = 2
        inner_schema = handler(args[1]) if len(args) >= _min_args else core_schema.any_schema()

        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.list_schema(inner_schema),
            serialization=core_schema.plain_serializer_function_ser_schema(list),
        )
