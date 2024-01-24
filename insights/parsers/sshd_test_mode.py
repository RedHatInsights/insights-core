"""
SshdTestMode - command ``sshd -T``
==================================

This module contains parsers that check the output of "/usr/sbin/sshd -T" command.

"""
from insights.core import Parser
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.sshd_test_mode)
class SshdTestMode(Parser, dict):
    """
    This parser reads the output of "/usr/sbin/sshd -T" command.

    Sample output::

        port 22
        addressfamily any
        listenaddress [::]:22
        listenaddress 0.0.0.0:22
        usepam yes
        logingracetime 120
        x11displayoffset 10
        x11maxdisplays 1000
        maxauthtries 6
        ciphers aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr
        macs hmac-sha2-256-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha1,umac-128@openssh.com,hmac-sha2-512

    Examples:
        >>> len(sshd_test_mode)
        10
        >>> sshd_test_mode.get("listenaddress")
        ['[::]:22', '0.0.0.0:22']
        >>> sshd_test_mode.get("ciphers")
        ['aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes128-gcm@openssh.com,aes128-ctr']
    """
    def parse_content(self, content):
        result = {}
        for line in get_active_lines(content):
            key, value = line.split(" ", 1)
            if key in result:
                result[key].append(value)
            else:
                result[key] = [value]
        self.update(result)
