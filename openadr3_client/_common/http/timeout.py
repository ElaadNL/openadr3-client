# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Timeout settings for HTTP requests made by the client."""

import math

type HttpTimeout = float | tuple[float, float]
"""Timeout setting for HTTP requests made by the client, in seconds.

A single number is used as both the connect and the read timeout. A ``(connect, read)`` tuple sets
them separately. ``None`` (wait indefinitely) is deliberately not supported: a VTN or authorization
server that stops responding must never block the caller forever.

When a timeout is exceeded, ``requests.exceptions.Timeout`` (``ConnectTimeout`` or ``ReadTimeout``)
is raised.
"""

DEFAULT_HTTP_TIMEOUT: HttpTimeout = 30.0
"""Default timeout, in seconds, applied to every HTTP request made by the client."""


def _validate_seconds(value: object, name: str) -> float:
    # bool is a subclass of int, but True/False as a timeout is almost certainly a mistake.
    if isinstance(value, bool) or not isinstance(value, int | float):
        msg = f"{name} must be a number of seconds, got {value!r}."
        raise TypeError(msg)
    if not math.isfinite(value) or value <= 0:
        msg = f"{name} must be a finite number of seconds greater than 0, got {value!r}."
        raise ValueError(msg)
    return float(value)


def validate_http_timeout(timeout: HttpTimeout) -> HttpTimeout:
    """
    Validate an HTTP timeout setting.

    Args:
        timeout: The timeout to validate. See `HttpTimeout`.

    Returns:
        The validated timeout, with numbers normalized to ``float``.

    Raises:
        TypeError: If the timeout is ``None``, or is not a number or a ``(connect, read)`` tuple of numbers.
        ValueError: If any timeout value is not a finite number greater than 0.

    """
    if timeout is None:
        msg = "timeout must not be None: waiting indefinitely for a response is not supported. Pass a number of seconds or a (connect, read) tuple."
        raise TypeError(msg)
    if isinstance(timeout, tuple):
        if len(timeout) != 2:  # noqa: PLR2004
            msg = f"timeout tuple must be (connect, read), got {timeout!r}."
            raise ValueError(msg)
        return (_validate_seconds(timeout[0], "connect timeout"), _validate_seconds(timeout[1], "read timeout"))
    return _validate_seconds(timeout, "timeout")
