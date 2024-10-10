"""
Parsers for RHC
===============

This module contains the following parsers:

RhcConf - file ``/etc/rhc/config.toml``
---------------------------------------
"""

from insights import Parser, parser
from insights.parsers import get_active_lines
from insights.specs import Specs
from insights.core.dr import SkipComponent


@parser(Specs.rhc_conf)
class RhcConf(Parser, dict):
    """
    Class to parse the ``/etc/rhc/config.toml`` configuration file.

    It's better to use the built-in "tomllib" lib to parse it after abandoning the support
    of versions before python3.11.
    But now to avoid reinvent the wheel, we just parse the filtered lines of simple key-value
    pairs and does not consider section and muli-lines.

    Sample input::

        broker = ["wss://connect.cloud.redhat.com:443"]
        cert-file = "/etc/pki/consumer/cert.pem"
        "key-file" = "/etc/pki/consumer/key.pem"
        log-level = "error"

    Raises:
        SkipComponent: No available data

    Examples:
        >>> type(rhc_conf)
        <class 'insights.parsers.rhc.RhcConf'>
        >>> 'mqtt-reconnect-delay' in rhc_conf
        False
        >>> 'log-level' in rhc_conf
        True
        >>> rhc_conf['log-level']
        'error'
    """

    def parse_content(self, content):
        for line in get_active_lines(content):
            if '=' in line:
                k, v = [i.strip('"\' ') for i in line.split('=', 1)]
                self[k] = v
        if not self:
            raise SkipComponent
