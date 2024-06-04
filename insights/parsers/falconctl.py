"""
Parsers for ``falconctl`` command outputs
=========================================

This module provides the following parsers:

FalconctlBackend - command ``/opt/CrowdStrike/falconctl -g --backend``
----------------------------------------------------------------------

FalconctlRfm - command ``/opt/CrowdStrike/falconctl -g --rfm-state``
--------------------------------------------------------------------

FalconctlAid - command ``/opt/CrowdStrike/falconctl -g --aid``
--------------------------------------------------------------

FalconctlVersion - command ``/opt/CrowdStrike/falconctl -g --version``
----------------------------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent, ParseException
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
        if len(content) == 1 and "=" in content[0]:
            self.backend = content[0].split(".")[0].split("=")[-1].strip()
        elif len(content) == 1 and " is not set." in content[0]:
            self.backend = "not set"

        if not self.backend:
            raise ParseException("Invalid content: {0}".format(content))


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


@parser(Specs.falconctl_aid)
class FalconctlAid(CommandParser):
    """
    This parser reads the output of ``/opt/CrowdStrike/falconctl -g --aid``,
    return the agent id as a string.

    Example output::

        aid="44e3b7d20b434a2bb2815d9808fa3a8b".

    Examples:
        >>> type(falconctlaid)
        <class 'insights.parsers.falconctl.FalconctlAid'>
        >>> falconctlaid.aid
        '44e3b7d20b434a2bb2815d9808fa3a8b'
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty.")

        self.aid = None
        if len(content) == 1 and "=" in content[0]:
            self.aid = content[0].split(".")[0].split("=")[-1].strip('" ')
        elif len(content) == 1 and " is not set." in content[0]:
            self.aid = "not set"

        if not self.aid:
            raise ParseException("Invalid content: {0}".format(content))


@parser(Specs.falconctl_version)
class FalconctlVersion(CommandParser):
    """
    This parser reads the output of ``/opt/CrowdStrike/falconctl -g --version``,
    return the running falcon_sensor version.

    Example output::

        version = 7.14.16703.0

    Examples:
        >>> type(falconctlversion)
        <class 'insights.parsers.falconctl.FalconctlVersion'>
        >>> falconctlversion.version
        '7.14.16703.0'
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty.")

        self.version = None
        if "=" in content[0]:
            self.version = content[0].split("=")[-1].strip()

        if not self.version:
            raise ParseException("Invalid content: {0}".format(content))
