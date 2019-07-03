"""
SetupNamedChroot - file ``/usr/libexec/setup-named-chroot.sh``
==============================================================

This module provides class ``SetupNamedChroot`` for parsing the output of file
``/usr/libexec/setup-named-chroot.sh``.
"""

from insights import LegacyItemAccess, Parser, get_active_lines, parser
from insights.core.filters import add_filter
from insights.parsers import SkipException
from insights.specs import Specs

add_filter(Specs.setup_named_chroot, ["ROOTDIR_MOUNT", "/"])


@parser(Specs.setup_named_chroot)
class SetupNamedChroot(Parser, LegacyItemAccess):
    """
    Class for parsing the `/usr/libexec/setup-named-chroot.sh` file.

    Typical content of the filtered file is::

        #!/bin/bash
        # it MUST be listed last. (/var/named contains /var/named/chroot)
        ROOTDIR_MOUNT='/etc/localtime /etc/named /etc/pki/dnssec-keys /etc/named.root.key /etc/named.conf
        /etc/named.dnssec.keys /etc/named.rfc1912.zones /etc/rndc.conf /etc/rndc.key /usr/lib64/bind
        /usr/lib/bind /etc/named.iscdlv.key /run/named /var/named /etc/protocols /etc/services'
            for all in $ROOTDIR_MOUNT; do
            for all in $ROOTDIR_MOUNT; do,
            # Check if file is mount target. Do not use /proc/mounts because detecting

    Examples:
        >>> len(snc.data)
        2
        >>> snc['ROOTDIR_MOUNT']
        '/etc/localtime /etc/named /etc/pki/dnssec-keys /etc/named.root.key /etc/named.conf /etc/named.dnssec.keys /etc/named.rfc1912.zones /etc/rndc.conf /etc/rndc.key /etc/named.iscdlv.key /etc/protocols /etc/services /usr/lib64/bind /usr/lib/bind /run/named /var/named'
    """

    def parse_content(self, content):
        # No content found or file is empty
        if not content:
            raise SkipException("Empty file")

        self.data = {}
        key, value = "", ""
        for line in get_active_lines(content):
            if "=" in line:
                key, value = line.split("=", 1)
            elif key:
                if value.endswith("'") or value.endswith("\""):
                    self.data[key] = value[1:-1]
                    key, value = "", ""
                value = value + " " + line
