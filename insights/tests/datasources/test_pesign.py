import pytest

from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.pesign import LocalSpecs, pesign_show_signature_shimx64


# Template for multi-cert output
PESIGN_OUTPUT_MULTI_CERT_TEMP = """
---------------------------------------------
The signer's common name is Microsoft Corporation UEFI CA 2011{sign_email_1}
Signing time: Jul  7, 2011
There is a valid signature.
MD: SHA256   Signature: RSA pkcs1 padding
---------------------------------------------
The signer's common name is Microsoft Corporation UEFI CA 2023{sign_email_2}
Signing time: Sep 21, 2015
There is a valid signature.
MD: SHA256   Signature: RSA pkcs1 padding
---------------------------------------------
""".strip()

PESIGN_OUTPUT_MULTI_CERT_ORG = PESIGN_OUTPUT_MULTI_CERT_TEMP.format(
    sign_email_1="\nThe signer's email address is secure@microsoft.com",
    sign_email_2="\nThe signer's email address is secure@microsoft.com"
)

PESIGN_OUTPUT_MULTI_CERT_FILTERED = PESIGN_OUTPUT_MULTI_CERT_TEMP.format(
    sign_email_1="",
    sign_email_2=""
)

# Template for single-cert output
PESIGN_OUTPUT_SINGLE_CERT_TEMP = """
---------------------------------------------
The signer's common name is Red Hat Secure Boot (CA key 1){sign_email}
Signing time: May 12, 2020
There is a valid signature.
MD: SHA256   Signature: RSA pkcs1 padding
---------------------------------------------
""".strip()

PESIGN_OUTPUT_SINGLE_CERT_ORG = PESIGN_OUTPUT_SINGLE_CERT_TEMP.format(
    sign_email="\nThe signer's email address is secalert@redhat.com"
)

PESIGN_OUTPUT_SINGLE_CERT_FILTERED = PESIGN_OUTPUT_SINGLE_CERT_TEMP.format(
    sign_email=""
)

# Template for custom cert output
PESIGN_OUTPUT_CUSTOM_CERT_TEMP = """
---------------------------------------------
The signer's common name is Custom Enterprise CA{sign_email}
Signing time: Jan 15, 2023
There is a valid signature.
MD: SHA256   Signature: RSA pkcs1 padding
---------------------------------------------
""".strip()

PESIGN_OUTPUT_CUSTOM_CERT_ORG = PESIGN_OUTPUT_CUSTOM_CERT_TEMP.format(
    sign_email="\nThe signer's email address is john.doe@customcompany.com"
)

PESIGN_OUTPUT_CUSTOM_CERT_FILTERED = PESIGN_OUTPUT_CUSTOM_CERT_TEMP.format(
    sign_email=""
)

# Only email lines (edge case)
PESIGN_OUTPUT_ONLY_EMAIL = """
The signer's email address is test@example.com
""".strip()


class MockRawOutput:
    """Mock raw command output"""
    def __init__(self, output):
        self.content = output.splitlines() if output else []


def test_pesign_success_multi_cert():
    """Test successful filtering with multiple certificates"""
    raw_output = MockRawOutput(PESIGN_OUTPUT_MULTI_CERT_ORG)
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    result = pesign_show_signature_shimx64(broker)

    assert result is not None
    assert isinstance(result, DatasourceProvider)

    content_str = "\n".join(result.content)
    assert content_str == PESIGN_OUTPUT_MULTI_CERT_FILTERED


def test_pesign_success_single_cert():
    """Test successful filtering with single certificate"""
    raw_output = MockRawOutput(PESIGN_OUTPUT_SINGLE_CERT_ORG)
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    result = pesign_show_signature_shimx64(broker)

    assert result is not None
    assert isinstance(result, DatasourceProvider)

    content_str = "\n".join(result.content)
    assert content_str == PESIGN_OUTPUT_SINGLE_CERT_FILTERED


def test_pesign_filters_custom_email():
    """Test that custom/private email addresses are filtered"""
    raw_output = MockRawOutput(PESIGN_OUTPUT_CUSTOM_CERT_ORG)
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    result = pesign_show_signature_shimx64(broker)

    assert result is not None
    assert isinstance(result, DatasourceProvider)

    content_str = "\n".join(result.content)
    assert content_str == PESIGN_OUTPUT_CUSTOM_CERT_FILTERED


def test_pesign_no_output():
    """Test SkipComponent when no raw output available"""
    raw_output = MockRawOutput(None)
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    with pytest.raises(SkipComponent) as exc:
        pesign_show_signature_shimx64(broker)

    assert "No pesign output available" in str(exc.value)


def test_pesign_empty_output():
    """Test SkipComponent when raw output is empty"""
    raw_output = MockRawOutput("")
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    with pytest.raises(SkipComponent) as exc:
        pesign_show_signature_shimx64(broker)

    assert "No pesign output available" in str(exc.value)


def test_pesign_only_email_lines():
    """Test SkipComponent when only email lines present (all filtered out)"""
    raw_output = MockRawOutput(PESIGN_OUTPUT_ONLY_EMAIL)
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    with pytest.raises(SkipComponent) as exc:
        pesign_show_signature_shimx64(broker)

    assert "No output after filtering email lines" in str(exc.value)


def test_pesign_case_insensitive_filtering():
    """Test that email filtering is case-insensitive"""
    output_org = """The signer's EMAIL ADDRESS is test@example.com
The signer's Email Address is another@example.com
Some other line"""

    output_expected = "Some other line"

    raw_output = MockRawOutput(output_org)
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    result = pesign_show_signature_shimx64(broker)

    content_str = "\n".join(result.content)
    assert content_str == output_expected


def test_pesign_relative_path():
    """Test that the correct relative path is set"""
    raw_output = MockRawOutput(PESIGN_OUTPUT_SINGLE_CERT_ORG)
    broker = {LocalSpecs.pesign_show_signature_shimx64_raw: raw_output}

    result = pesign_show_signature_shimx64(broker)

    assert result.relative_path == "insights_commands/pesign_show_signature_shimx64"
