from unittest.mock import patch

import pytest

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.specs.datasources.pesign import SHIM_PATH, shim_certs

SHOW_SIGNATURE = [
    "context of signing event",
    "  certificate address is 0x1111",
    "  digest algorithm: sha256",
    "context of signing event",
    "  certificate address is 0x2222",
    "  digest algorithm: sha256",
]

SHOW_SIGNATURE_NO_CERTS = [
    "no signatures found",
]

CERT_INFO_0 = [
    "Certificate:",
    "    Data:",
    "        Serial Number: 1 (0x1)",
    "        Issuer: C=US, O=Red Hat, Inc., CN=Red Hat Secure Boot CA",
    "        Validity",
    "            Not Before: Jan  1 00:00:00 2020 GMT",
    "            Not After : Jan  1 00:00:00 2030 GMT",
    "        Subject: C=US, O=Red Hat, Inc., CN=Red Hat Test Cert",
]

CERT_INFO_1 = [
    "Certificate:",
    "        Issuer: C=US, O=Microsoft Corporation, CN=Microsoft UEFI CA",
    "            Not Before: Jan  1 00:00:00 2021 GMT",
    "            Not After : Jan  1 00:00:00 2031 GMT",
    "        Subject: C=US, O=Microsoft Corporation, CN=Microsoft Test Cert",
]

TWO_CERTS_SUCCESS_OUTPUT = """
=== signum 0 ===
        Issuer: C=US, O=Red Hat, Inc., CN=Red Hat Secure Boot CA
            Not Before: Jan  1 00:00:00 2020 GMT
            Not After : Jan  1 00:00:00 2030 GMT
        Subject: C=US, O=Red Hat, Inc., CN=Red Hat Test Cert
=== signum 1 ===
        Issuer: C=US, O=Microsoft Corporation, CN=Microsoft UEFI CA
            Not Before: Jan  1 00:00:00 2021 GMT
            Not After : Jan  1 00:00:00 2031 GMT
        Subject: C=US, O=Microsoft Corporation, CN=Microsoft Test Cert
""".strip()

ONE_CERT_SKIPPED_OUTPUT = """
=== signum 1 ===
        Issuer: C=US, O=Microsoft Corporation, CN=Microsoft UEFI CA
            Not Before: Jan  1 00:00:00 2021 GMT
            Not After : Jan  1 00:00:00 2031 GMT
        Subject: C=US, O=Microsoft Corporation, CN=Microsoft Test Cert
""".strip()

ONE_CERT_OPENSSL_FAIL_OUTPUT = """
=== signum 0 ===
        Issuer: C=US, O=Red Hat, Inc., CN=Red Hat Secure Boot CA
            Not Before: Jan  1 00:00:00 2020 GMT
            Not After : Jan  1 00:00:00 2030 GMT
        Subject: C=US, O=Red Hat, Inc., CN=Red Hat Test Cert
""".strip()


@patch("os.path.exists", return_value=False)
def test_no_shim_file(m_exists):
    broker = {HostContext: HostContext()}
    with pytest.raises(SkipComponent):
        shim_certs(broker)
    m_exists.assert_called_once_with(SHIM_PATH)


@patch("insights.specs.datasources.pesign.HostContext.shell_out", return_value=(1, []))
@patch("os.path.exists", return_value=True)
def test_show_signature_fails(m_exists, m_shell_out):
    broker = {HostContext: HostContext()}
    with pytest.raises(SkipComponent):
        shim_certs(broker)
    m_shell_out.assert_called_once()


@patch(
    "insights.specs.datasources.pesign.HostContext.shell_out",
    return_value=(0, SHOW_SIGNATURE_NO_CERTS),
)
@patch("os.path.exists", return_value=True)
def test_no_certificates_found(m_exists, m_shell_out):
    broker = {HostContext: HostContext()}
    with pytest.raises(SkipComponent):
        shim_certs(broker)
    m_shell_out.assert_called_once()


@patch("os.path.exists", return_value=True)
@patch("insights.specs.datasources.pesign.HostContext.shell_out")
def test_valid_two_signatures(m_shell_out, m_exists):
    broker = {HostContext: HostContext()}
    m_shell_out.side_effect = [
        (0, SHOW_SIGNATURE),
        (0, []),  # pesign export signum 0
        (0, CERT_INFO_0),  # openssl signum 0
        (0, []),  # pesign export signum 1
        (0, CERT_INFO_1),  # openssl signum 1
    ]
    result = shim_certs(broker)

    text_result = "\n".join(result.content)
    assert TWO_CERTS_SUCCESS_OUTPUT == text_result
    assert m_shell_out.call_count == 5


@patch("os.path.exists", return_value=True)
@patch("insights.specs.datasources.pesign.HostContext.shell_out")
def test_export_failure_for_one_signature_is_skipped(m_shell_out, m_exists):
    broker = {HostContext: HostContext()}
    m_shell_out.side_effect = [
        (0, SHOW_SIGNATURE),
        (1, []),  # pesign export signum 0 fails
        (0, []),  # pesign export signum 1
        (0, CERT_INFO_1),  # openssl signum 1
    ]
    result = shim_certs(broker)

    text_result = "\n".join(result.content)
    assert ONE_CERT_SKIPPED_OUTPUT == text_result
    assert m_shell_out.call_count == 4


@patch("os.path.exists", return_value=True)
@patch("insights.specs.datasources.pesign.HostContext.shell_out")
def test_openssl_failure_for_one_signature_is_skipped(m_shell_out, m_exists):
    broker = {HostContext: HostContext()}
    m_shell_out.side_effect = [
        (0, SHOW_SIGNATURE),
        (0, []),  # pesign export signum 0
        (0, CERT_INFO_0),  # openssl signum 0
        (0, []),  # pesign export signum 1
        (1, []),  # openssl signum 1 fail
    ]
    result = shim_certs(broker)

    text_result = "\n".join(result.content)
    assert ONE_CERT_OPENSSL_FAIL_OUTPUT == text_result
    assert m_shell_out.call_count == 5


@patch("os.path.exists", return_value=True)
@patch(
    "insights.specs.datasources.pesign.HostContext.shell_out",
    side_effect=Exception("unexpected_exception"),
)
def test_unexpected_exception_is_skipped(m_shell_out, m_exists):
    broker = {HostContext: HostContext()}
    with pytest.raises(SkipComponent):
        shim_certs(broker)
