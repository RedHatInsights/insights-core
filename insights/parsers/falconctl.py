"""
Parsers for ``falconctl`` command outputs
=========================================

This module provides the following parsers:

FalconctlBackend - command ``/opt/CrowdStrike/falconctl -g --backend``
----------------------------------------------------------------------

FalconctlRfm - command ``/opt/CrowdStrike/falconctl -g --rfm-state``
--------------------------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.falconctl_backend)
class FalconctlBackend(CommandParser):
    """
    This parser reads the output of ``/opt/CrowdStrike/falconctl -g --backend``,
    return the back-end mode as a string.

    Example output::

        backend is not set.
        or
        backend=auto.

    Examples:
        >>> type(falconctlbackend)
        <class 'insights.parsers.falconctl.FalconctlBackend'>
        >>> falconctlbackend.backend
        'auto'

    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty.")
        self.backend = ""
        if "=" in content[0]:
            self.backend = content[0].split(".")[0].split("=")[-1].strip()
        else:
            self.backend = "not set"


@parser(Specs.falconctl_rfm)
class FalconctlRfm(CommandParser):
    """
    This parser reads the output of ``/opt/CrowdStrike/falconctl -g --rfm-state``,
    return the Reduced Functionality Mode as boolean.

    Example output::

        rfm-state=false.

    Examples:
        >>> type(falconctlrfm)
        <class 'insights.parsers.falconctl.FalconctlRfm'>
        >>> falconctlrfm.rfm
        False

    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty.")
        self.rfm = False
        state = content[0].split(".")[0].split("=")[-1].strip()
        if state == "true":
            self.rfm = True
