# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for the TLS verification settings at the public API boundary."""

from pathlib import Path

import pytest

from openadr3_client._common.http.authenticated_session import HTTPSOnlySession
from openadr3_client._common.tls import normalize_tls_verification


@pytest.mark.parametrize("verify_tls_certificate", [True, False])
def test_normalize_passes_booleans_through(verify_tls_certificate: bool) -> None:  # noqa: FBT001
    """Test that boolean verification settings are returned unchanged."""
    assert normalize_tls_verification(verify_tls_certificate) is verify_tls_certificate


def test_normalize_passes_path_through() -> None:
    """Test that a Path to a CA certificate bundle is returned unchanged."""
    ca_bundle = Path("/etc/ssl/certs/ca-bundle.pem")
    assert normalize_tls_verification(ca_bundle) == ca_bundle


def test_normalize_converts_deprecated_str_to_path() -> None:
    """Test that a deprecated str path is converted to a Path and warns about the deprecation."""
    with pytest.warns(DeprecationWarning, match="pass a pathlib.Path instead"):
        result = normalize_tls_verification("/etc/ssl/certs/ca-bundle.pem")

    assert result == Path("/etc/ssl/certs/ca-bundle.pem")


def test_normalize_rejects_empty_str() -> None:
    """Test that an empty string is rejected, as it would silently disable TLS verification."""
    with pytest.raises(ValueError, match="must not be an empty string"):
        normalize_tls_verification("")


def test_session_receives_ca_bundle_path_as_str() -> None:
    """Test that a Path reaches requests as a str, since requests types Session.verify as bool | str."""
    session = HTTPSOnlySession(verify_tls_certificate=Path("/etc/ssl/certs/ca-bundle.pem"))
    assert session.verify == "/etc/ssl/certs/ca-bundle.pem"
    assert isinstance(session.verify, str)


@pytest.mark.parametrize("verify_tls_certificate", [True, False])
def test_session_receives_boolean_verification_setting(verify_tls_certificate: bool) -> None:  # noqa: FBT001
    """Test that a boolean verification setting is applied to the session as-is."""
    session = HTTPSOnlySession(verify_tls_certificate=verify_tls_certificate)
    assert session.verify is verify_tls_certificate
