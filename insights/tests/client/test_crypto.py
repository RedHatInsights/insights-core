import os.path
import shutil
import subprocess
import tempfile

import mock
import pytest

from insights.client import crypto


# GPG2 exports keys in a way gpg1.4 cannot read. Since gpg1.4 is present in the
# Ubuntu image that is used in CI to test Python 2.6, we have to use the old
# version, so it is recognised by all CI branches.
#
# $ gpg --gen-key            # gpg1.x
# $ gpg --full-generate-key  # gpg2.x
# $ gpg --list-secret-keys --keyid-format long
# $ KEYID=xxx (line `sec`, after the `/` character)
# $ gpg --armor --export $KEYID
# $ gpg --armor --export-secret-keys $KEYID

GPG_PUBLIC_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1

mQENBGUlPEcBCACXhinLd4KiyQ9CWXM+gpgo0HMuTdESTlVVDYRjm/ebazephXq7
0hhAhXallAQJkaXFPuLETumwFYPx60agUDWsUie8gk3TLE+ejuTxoda0Yo6rehsD
zds1ptHQLzar00SFUlfiJXnMaobXLeNjDSglkynQC4uQODouDa1jkSRfNbDJOJYd
IBbPBIaJ3PlNrdVutPcx4yIZM1siqMZ9k0g2iYPWyp0ceuP0jpCTPc5TRRP5pLuz
INRJzhfJ+oPtbFt8Y4s1xEZ0Kfy0sA8Awk3VJqzoCU3ILBU5cGquQDdNggxTRSPV
X5Z4nW2zjN9lXAkwr29NL1rA1jjLt+c5upYZABEBAAG0SGluc2lnaHRzLWNvcmUg
KFNpZ25pbmcga2V5IGZvciB1bml0IHRlc3RpbmcpIDxpbnNpZ2h0cy1jb3JlQGV4
YW1wbGUub3JnPokBOAQTAQIAIgUCZSU8RwIbAwYLCQgHAwIGFQgCCQoLBBYCAwEC
HgECF4AACgkQn+6Vu126uXAHdgf/Q8a7Jruhyn+EDLL94gAc6kXubvVArVe9Rdpo
HwG7cj8wUa/7zd7FUcYJuz6bbebgmmlRwFf1CeodGURFpfwf1dkiKV5QqobeXhRp
srrkeLlMR8bZVFSCvU+oOETpJfMo6feDI/tQrOcIpxrd/cEu2XSQ1JBM/+8NbQiU
Ma1cWHOmQJ1OD7jWOllUq5hDs1vtUzPORUsYe1V1Dcx89gdlhfc1cc30yoLzDNqu
0Abn34CAthUkr0sWplzltXOY+Za1kOmQVlaLQ0W3tq8BDi79bdHpTtD/g9QO++Nc
r5xdP+tPNWAOUlyi7S6qscDLhMWv7o4eLq6UL9eUC/M2CWJSKg==
=9pSV
-----END PGP PUBLIC KEY BLOCK-----
"""

GPG_PRIVATE_KEY = """-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG v1

lQOYBGUlPEcBCACXhinLd4KiyQ9CWXM+gpgo0HMuTdESTlVVDYRjm/ebazephXq7
0hhAhXallAQJkaXFPuLETumwFYPx60agUDWsUie8gk3TLE+ejuTxoda0Yo6rehsD
zds1ptHQLzar00SFUlfiJXnMaobXLeNjDSglkynQC4uQODouDa1jkSRfNbDJOJYd
IBbPBIaJ3PlNrdVutPcx4yIZM1siqMZ9k0g2iYPWyp0ceuP0jpCTPc5TRRP5pLuz
INRJzhfJ+oPtbFt8Y4s1xEZ0Kfy0sA8Awk3VJqzoCU3ILBU5cGquQDdNggxTRSPV
X5Z4nW2zjN9lXAkwr29NL1rA1jjLt+c5upYZABEBAAEAB/0QIdsaTA+PCEwFGuPv
sFTF56eTsvpC8i8YnpdNSaI7nFcxR8JQ8+XcHLmMmG0znZuiG/dlwicUNb42CAAd
ely0i4yqf88MYCfb8EfEyB/FVcbtz9LHfWfM1wV4nkY6VgRyE1nC/I1yq5bOmxae
CZ0QHxJxEYGa6bmcBJ3Ev4O5VSKZRRByPI0HXmVB6GoqVtmwa7TFrlgLM5GPbgVe
P76lNY2me8jEnHqzrPpuCB/N0VSCEUf45RV+TNjWL1lpF8JPzXS8oGoxcDoo+sIQ
AdcfMFrRtf3DW8kJRZC8i4T9++/k3Sjak9GE8ocekCDJkFPRkKv3A4T8nvmMKbNx
fugZBADAGD+u4Uhwlyzvr84wmwIPcozhQhTWot8dom6LCiZ47sfyG1qVhvxqDKtc
ttPv+VfA0RyJb9PUKbOf71hA7lMm0qHyX6KTknYYl8u+s/ra8VSwdNyl2/DQDf2j
OjnIMLM9IC6TMQ/mvpvRmXLc6m6HfL6ZBAbAL0EwOMUAUelnBQQAye626NZJTZ3E
mQ9z6l6UEi3IZIw+uJfSg/HL4MgU4zRNsOqyJyizdmVzQm0h+1aHQu1SuFsllPXF
DOKR/IlkjQJCbiU1wZASYYJuwmmVdG4HqZD0bjKU40fJgzBJhOfnhi079jnZzMsL
+NltcmAtUFKteWsPZe7Blic4QmIbtwUEAIick2Ai788yKGrAry5XBwHNcSIYKNr2
FFWwjFQWAK82hG2tiKCtF8vg58KBvGR3KNUlCLqDeP85jK7+IuaExSlWKYxIKo70
8Vfpqpyol/+V1yZ2duEcPSXtrMTg5Yl/7PITyGPnM4mFjvwg+cuYRDqYTT0kWbrl
WxtODNwtZdIURTm0SGluc2lnaHRzLWNvcmUgKFNpZ25pbmcga2V5IGZvciB1bml0
IHRlc3RpbmcpIDxpbnNpZ2h0cy1jb3JlQGV4YW1wbGUub3JnPokBOAQTAQIAIgUC
ZSU8RwIbAwYLCQgHAwIGFQgCCQoLBBYCAwECHgECF4AACgkQn+6Vu126uXAHdgf/
Q8a7Jruhyn+EDLL94gAc6kXubvVArVe9RdpoHwG7cj8wUa/7zd7FUcYJuz6bbebg
mmlRwFf1CeodGURFpfwf1dkiKV5QqobeXhRpsrrkeLlMR8bZVFSCvU+oOETpJfMo
6feDI/tQrOcIpxrd/cEu2XSQ1JBM/+8NbQiUMa1cWHOmQJ1OD7jWOllUq5hDs1vt
UzPORUsYe1V1Dcx89gdlhfc1cc30yoLzDNqu0Abn34CAthUkr0sWplzltXOY+Za1
kOmQVlaLQ0W3tq8BDi79bdHpTtD/g9QO++Ncr5xdP+tPNWAOUlyi7S6qscDLhMWv
7o4eLq6UL9eUC/M2CWJSKg==
=ZQ6H
-----END PGP PRIVATE KEY BLOCK-----
"""

GPG_FINGERPRINT = "E884 7216 86A8 1EE3 EBF4  5771 9FEE 95BB 5DBA B970"
GPG_OWNER = (
    "insights-core (Signing key for unit testing) "
    "<insights-core@example.org>"
)


def _initialize_gpg_environment(home):
    """Save GPG keys and sign a file with them.

    The home directory is populated with the following files:
    - key.public.gpg
    - key.private.gpg
    - file.txt
    - file.txt.asc
    """
    # Save the public key into temporary file
    public_key = home + "/key.public.gpg"
    with open(public_key, "w") as f:
        f.write(GPG_PUBLIC_KEY)
    # It is strictly not necessary to import both public and private keys,
    #  the private key should be enough.
    #  However, the Python 2.6 CI image requires that.
    process = subprocess.Popen(
        ["/usr/bin/gpg", "--homedir", home, "--import", public_key],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"LC_ALL": "C.UTF-8"},
    )
    process.communicate()
    assert process.returncode == 0

    # Save the private key into temporary file and import it
    private_key = home + "/key.private.gpg"
    with open(private_key, "w") as f:
        f.write(GPG_PRIVATE_KEY)
    process = subprocess.Popen(
        ["/usr/bin/gpg", "--homedir", home, "--import", private_key],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"LC_ALL": "C.UTF-8"},
    )
    process.communicate()
    assert process.returncode == 0

    # Create a file and sign it
    file = home + "/file.txt"
    with open(file, "w") as f:
        f.write("a signed message")
    process = subprocess.Popen(
        ["/usr/bin/gpg", "--homedir", home, "--detach-sign", "--armor", file],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"LC_ALL": "C.UTF-8"},
    )
    process.communicate()
    assert process.returncode == 0

    # Ensure the signature has been created
    assert os.path.exists(home + "/file.txt.asc")


@mock.patch("insights.client.crypto.GPGCommand.TEMPORARY_GPG_HOME_PARENT_DIRECTORY", "/tmp/")
def test_valid_signature():
    """A detached file signature can be verified."""
    home = tempfile.mkdtemp()
    _initialize_gpg_environment(home)

    # Run the test
    result = crypto.verify_gpg_signed_file(
        file=home + "/file.txt",
        signature=home + "/file.txt.asc",
        key=home + "/key.public.gpg",
    )
    shutil.rmtree(home, ignore_errors=True)

    # Verify results
    assert True is result.ok
    assert "" == result.stdout
    assert (
        'gpg: Good signature from "{owner}"'.format(owner=GPG_OWNER)
    ) in result.stderr
    assert (
        'Primary key fingerprint: {fp}'.format(fp=GPG_FINGERPRINT)
    ) in result.stderr
    assert 0 == result.return_code

    assert not os.path.isfile(result._command._home)


@pytest.mark.parametrize("file", ("/file.txt", "/file.txt.asc"))
def test_no_file(file):
    """Missing file or its signature is caught and returned as command result."""
    home = tempfile.mkdtemp()
    _initialize_gpg_environment(home)

    os.remove(home + file)

    result = crypto.verify_gpg_signed_file(
        file=home + "/file.txt",
        signature=home + "/file.txt.asc",
        key=home + "/key.public.gpg",
    )

    assert not os.path.isfile(home + file)
    assert result.ok is False
    assert result.return_code > 0
    assert "file '{path}' does not exist".format(path=home + file) == result.stderr

    shutil.rmtree(home, ignore_errors=True)


@mock.patch("insights.client.crypto.GPGCommand.TEMPORARY_GPG_HOME_PARENT_DIRECTORY", "/tmp/")
def test_invalid_public_key():
    """Invalid key is rejected."""
    home = tempfile.mkdtemp()
    _initialize_gpg_environment(home)

    with open(home + "/key.public.gpg", "w") as f:
        f.write("instead of the key, this file contains garbage")

    result = crypto.verify_gpg_signed_file(
        file=home + "/file.txt",
        signature=home + "/file.txt.asc",
        key=home + "/key.public.gpg",
    )

    assert result.ok is False
    assert result.return_code > 0


@mock.patch("insights.client.crypto.GPGCommand.TEMPORARY_GPG_HOME_PARENT_DIRECTORY", "/tmp/")
def test_invalid_signature():
    """A bad detached file signature can be detected."""
    home = tempfile.mkdtemp()
    _initialize_gpg_environment(home)

    # Change the contents of the file, making the signature incorrect
    with open(home + "/file.txt", "w") as f:
        f.write("an unsigned message")

    # Run the test
    result = crypto.verify_gpg_signed_file(
        file=home + "/file.txt",
        signature=home + "/file.txt.asc",
        key=home + "/key.public.gpg",
    )
    shutil.rmtree(home, ignore_errors=True)

    # Verify results
    assert not result.ok
    assert "" == result.stdout
    assert (
        'gpg: BAD signature from "{owner}"'.format(owner=GPG_OWNER)
    ) in result.stderr
    assert (
        'Primary key fingerprint: {fp}'.format(fp=GPG_FINGERPRINT)
    ) not in result.stderr
    assert 1 == result.return_code

    assert not os.path.isfile(result._command._home)


GPG_VERSION_CENTOS7 = """gpg (GnuPG) 2.0.22
libgcrypt 1.5.3
Copyright (C) 2013 Free Software Foundation, Inc.
...
"""
GPG_VERSION_CENTOS8 = """gpg (GnuPG) 2.2.20
libgcrypt 1.8.5
Copyright (C) 2020 Free Software Foundation, Inc.
...
"""
GPG_VERSION_CENTOS9 = """gpg (GnuPG) 2.3.3
libgcrypt 1.10.0-unknown
Copyright (C) 2021 Free Software Foundation, Inc.
...
"""


@pytest.mark.parametrize("output,supports", [
    (GPG_VERSION_CENTOS7, False),
    (GPG_VERSION_CENTOS8, True),
    (GPG_VERSION_CENTOS9, True),
    ("garbage output", False),
    ("gpg (GnuPG) 2.8", False),
    ("gpg (GnuPG) 2.8.1a9", False),
])
@mock.patch("insights.client.crypto.GPGCommand.TEMPORARY_GPG_HOME_PARENT_DIRECTORY", "/tmp/")
def test_gpg_socket_cleanup_support(output, supports):
    home = tempfile.mkdtemp()

    command = crypto.GPGCommand(command=[], key="")
    command._home = home

    class MockPopen:
        def __init__(self, stdout):
            self.stdout = stdout
            self.returncode = 0

        def communicate(self, *args, **kwargs):
            return self.stdout, ""

    with mock.patch("insights.client.crypto.subprocess.Popen", return_value=MockPopen(stdout=output)):
        result = command._supports_cleanup_socket()

    assert result == supports


@mock.patch("insights.client.crypto.GPGCommand.TEMPORARY_GPG_HOME_PARENT_DIRECTORY", "/tmp/")
@mock.patch("subprocess.Popen")
@mock.patch.object(crypto.GPGCommand, "_cleanup", return_value=None)
def test_invalid_gpg_setup(mock_cleanup, mock_popen):
    """An invalid GPG setup can be detected."""
    gpg_command = crypto.GPGCommand(command=[], key=os.path.join("/dummy", "key"))

    # Mock the process
    mock_process = mock.Mock()
    mock_process.communicate.return_value = (b"", b"gpg setup failed")
    mock_process.returncode = 1
    mock_popen.return_value = mock_process

    # Run the test
    result = gpg_command.evaluate()  # type: crypto.GPGCommandResult

    # Verify the results
    assert not result.ok
    assert "" == result.stdout
    assert "gpg setup failed" in result.stderr
    assert 1 == result.return_code
