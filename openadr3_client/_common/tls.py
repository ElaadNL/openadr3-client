# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""TLS certificate verification settings for connections to a VTN."""

import warnings
from pathlib import Path

type TlsVerification = bool | Path
"""TLS certificate verification setting for connections to a VTN.

``True`` validates the TLS certificate of the VTN against the known CAs. ``False`` disables
verification entirely, which is not recommended outside of development or test environments.

A ``Path`` points to a custom CA certificate bundle (.PEM) for a self signed CA. The PEM file must
contain the entire certificate chain, including the intermediate certificates required to validate the
certificate of the VTN.
"""


def normalize_tls_verification(verify_tls_certificate: TlsVerification | str) -> TlsVerification:
    """
    Normalize a TLS verification setting given at the public API boundary.

    Converts a deprecated ``str`` path into a ``Path``, so that internal code only has to handle
    `TlsVerification`. Booleans and ``Path`` values are passed through unchanged.

    Args:
        verify_tls_certificate: The TLS verification setting to normalize. Passing a ``str`` path is
        deprecated, pass a `pathlib.Path` instead.

    Returns:
        The normalized TLS verification setting.

    Raises:
        ValueError: If an empty string is given. An empty string is falsy, which would silently disable
        TLS verification rather than point at a CA certificate bundle.

    """
    if isinstance(verify_tls_certificate, bool):
        return verify_tls_certificate
    if isinstance(verify_tls_certificate, str):
        if not verify_tls_certificate:
            msg = (
                "verify_tls_certificate must not be an empty string. Pass True to verify against the known CAs, "
                "False to disable verification, or a path to a custom CA certificate bundle."
            )
            raise ValueError(msg)
        warnings.warn(
            "Passing a str path as verify_tls_certificate is deprecated, pass a pathlib.Path instead.",
            DeprecationWarning,
            # Called directly from the public client factories, so this points at the caller of the factory.
            stacklevel=3,
        )
        return Path(verify_tls_certificate)
    return verify_tls_certificate
