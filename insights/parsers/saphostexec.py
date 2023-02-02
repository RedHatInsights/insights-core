"""
saphostexec - Commands
======================

Shared parsers for parsing output of the ``saphostexec [option]`` commands.

SAPHostExecStatus - command ``saphostexec -status``
---------------------------------------------------

SAPHostExecVersion - command ``saphostexec -version``
-----------------------------------------------------
"""
from collections import namedtuple

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.saphostexec_status)
class SAPHostExecStatus(CommandParser, dict):
    """
    Class for parsing the output of ``saphostexec -status`` command.

    Typical output of the command is::

        saphostexec running (pid = 9159)
        sapstartsrv running (pid = 9163)
        saposcol running (pid = 9323)

    Examples:
        >>> type(sha_status)
        <class 'insights.parsers.saphostexec.SAPHostExecStatus'>
        >>> sha_status.is_running
        True
        >>> sha_status.services['saphostexec'].status
        'running'
        >>> sha_status['saphostexec'].status
        'running'
        >>> sha_status['saphostexec'].pid
        '9159'
    """

    SAPHostAgentService = namedtuple("SAPHostAgentService", field_names=["status", "pid"])
    """namedtuple: Type for storing the lines of ``saphostexec -status``"""

    def parse_content(self, content):
        data = {}
        for line in content:
            if not line.strip():
                continue
            line_sp = line.strip().split(None, 1)
            if len(line_sp) == 2:
                value_sp = line_sp[1].replace('(', '').replace(')', '').split()
                svc, sta, pid = line_sp[0], value_sp[0], value_sp[-1]
                data[svc] = self.SAPHostAgentService(sta, pid)
            else:
                raise ParseException("Incorrect line: '{0}'".format(line))
        if data:
            self.update(data)
        else:
            raise SkipComponent

    @property
    def is_running(self):
        """
        Returns if the SAPHostAgent is running or not.
        """
        return all(p.status == 'running' for p in self.values())

    @property
    def data(self):
        """
        .. warning::

            Deprecated, the parser works as a dict please use the built-in
            accesses of `dict`

        Returns the parsed data.
        """
        return self

    @property
    def services(self):
        """
        Returns the parsed lines.
        """
        return self


@parser(Specs.saphostexec_version)
class SAPHostExecVersion(CommandParser, dict):
    """
    Class for parsing the output of ``saphostexec -version`` command.

    Typical output of the command is::

        *************************** Component ********************
        /usr/sap/hostctrl/exe/saphostexec: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 04:43:56)
        /usr/sap/hostctrl/exe/sapstartsrv: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 04:43:56)
        /usr/sap/hostctrl/exe/saphostctrl: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 04:43:56)
        /usr/sap/hostctrl/exe/xml71d.so: 721, patch 1011, changelist 1814854, linuxx86_64, opt (Jan 13 2018, 01:12:10)
        **********************************************************
        --------------------
        SAPHOSTAGENT information
        --------------------
        kernel release                721
        kernel make variant           721_REL
        compiled on                   Linux GNU SLES-9 x86_64 cc4.1.2  for linuxx86_64
        compiled for                  64 BIT
        compilation mode              Non-Unicode
        compile time                  Jan 13 2018 04:40:52
        patch number                  33
        latest change number          1814854
        ---------------------
        supported environment
        ---------------------
        operating system
        Linux 2.6
        Linux 3
        Linux

    Examples:
        >>> type(sha_version)
        <class 'insights.parsers.saphostexec.SAPHostExecVersion'>
        >>> sha_version.components['saphostexec'].version
        '721'
        >>> sha_version['saphostexec'].version
        '721'
        >>> sha_version['saphostexec'].patch
        '1011'
    """

    SAPHostAgentComponent = namedtuple("SAPHostAgentComponent",
            field_names=["version", "patch", "changelist"])
    """namedtuple: Type for storing the lines of ``saphostexec -version``"""

    def parse_content(self, content):
        data = {}
        for line in content:
            # Only process component lines for now
            if not line.startswith('/usr/sap/hostctrl/exe/'):
                continue
            key, val = line.split(':', 1)
            key = key.split('/')[-1]
            ver, pch, chl, _ = [s.split()[-1].strip() for s in val.split(', ', 3)]
            data[key] = self.SAPHostAgentComponent(ver, pch, chl)
        if data:
            self.update(data)
        else:
            raise SkipComponent

    @property
    def data(self):
        """
        .. warning::

            Deprecated, the parser works as a dict please use the built-in
            accesses of `dict`

        Returns the parsed data.
        """
        return self

    @property
    def components(self):
        """
        Return the dict of :py:class:`SAPHostAgentComponent` instances.
        """
        return self
