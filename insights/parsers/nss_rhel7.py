# -*- coding: utf-8 -*-
"""
NssRhel7 - file ``/etc/pki/nss-legacy/nss-rhel7.config``
========================================================
"""

from insights import parser, SysconfigOptions
from insights.specs import Specs


@parser(Specs.nss_rhel7)
class NssRhel7(SysconfigOptions):
    """
    This parser reads the ``/etc/pki/nss-legacy/nss-rhel7.config``
    file. It uses the ``SysconfigOptions`` parser class to convert the file into
    a dictionary of options. It also provides the ``config`` property as a helper
    to retrieve the ``config`` variable.

    Attributes:
        config (union[str, None]): The value of the ``config`` variable if it exists, else None.

    Sample Input::

        # To re-enable legacy algorithms, edit this file
        # Note that the last empty line in this file must be preserved
        library=
        name=Policy
        NSS=flags=policyOnly,moduleDB
        config="disallow=MD5:RC4 allow=DH-MIN=1023:DSA-MIN=1023:RSA-MIN=1023:TLS-VERSION-MIN=tls1.0"


    Examples:
        >>> 'config' in nss_rhel7
        True
        >>> nss_rhel7.config
        'disallow=MD5:RC4 allow=DH-MIN=1023:DSA-MIN=1023:RSA-MIN=1023:TLS-VERSION-MIN=tls1.0'
    """

    @property
    def config(self):
        return self.data.get("config", None)
