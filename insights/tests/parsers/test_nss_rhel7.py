# -*- coding: utf-8 -*-

import doctest

from insights.parsers import nss_rhel7
from insights.parsers.nss_rhel7 import NssRhel7
from insights.tests import context_wrap

NSS_RHEL7 = """
# To re-enable legacy algorithms, edit this file
# Note that the last empty line in this file must be preserved
library=
name=Policy
NSS=flags=policyOnly,moduleDB
config="disallow=MD5:RC4 allow=DH-MIN=1023:DSA-MIN=1023:RSA-MIN=1023:TLS-VERSION-MIN=tls1.0"
"""


def test_nss_rhel7():
    nss_rhel7 = NssRhel7(context_wrap(NSS_RHEL7))
    assert "config" in nss_rhel7
    assert "asdf" not in nss_rhel7
    assert (
        nss_rhel7.config == "disallow=MD5:RC4 allow=DH-MIN=1023:DSA-MIN=1023:RSA-MIN=1023:TLS-VERSION-MIN=tls1.0"
    )
    assert (
        nss_rhel7["config"] == "disallow=MD5:RC4 allow=DH-MIN=1023:DSA-MIN=1023:RSA-MIN=1023:TLS-VERSION-MIN=tls1.0"
    )
    assert (
        nss_rhel7.get("config") == "disallow=MD5:RC4 allow=DH-MIN=1023:DSA-MIN=1023:RSA-MIN=1023:TLS-VERSION-MIN=tls1.0"
    )
    assert nss_rhel7.get("asdf") is None


def test_doc_examples():
    env = {
        "nss_rhel7": NssRhel7(context_wrap(NSS_RHEL7)),
    }
    failed, total = doctest.testmod(nss_rhel7, globs=env)
    assert failed == 0
