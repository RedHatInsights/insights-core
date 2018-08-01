"""
saphostexec - Commands
======================

Shared parsers for parsing output of the ``saphostexec [option]`` commands.

SAPHostExecStatus- command ``saphostexec -status``
--------------------------------------------------

SAPHostExecVersion - command ``saphostexec -version``
-----------------------------------------------------
"""
from .. import parser, CommandParser, LegacyItemAccess
from insights.parsers import SkipException
from insights.specs import Specs
from collections import namedtuple


@parser(Specs.saphostexec_status)
class SAPHostExecStatus(CommandParser, LegacyItemAccess):
    """
    Class for parsing the output of `saphostexec -status` command.

    Typical output of the command is::

        saphostexec running (pid = 9159)
        sapstartsrv running (pid = 9163)
        saposcol running (pid = 9323)

    Attributes:
        is_running (bool): The SAP Host Agent is running or not.
        services (list): List of services.

    Examples:
        >>> type(sha_status)
        <class 'insights.parsers.saphostexec.SAPHostExecStatus'>
        >>> sha_status.is_running
        True
        >>> sha_status.services['saphostexec']
        '9159'
    """

    def parse_content(self, content):
        self.is_running = False
        self.services = self.data = {}
        if 'saphostexec stopped' not in content[0]:
            for line in content:
                line_splits = line.split()
                self.services[line_splits[0]] = ''
                if len(line_splits) == 5 and line_splits[1] == 'running':
                    self.services[line_splits[0]] = line_splits[-1][:-1]
                else:
                    raise SkipException("Incorrect status: '{0}'".format(line))

            self.is_running = self.services and all(p for p in self.services.values())


@parser(Specs.saphostexec_version)
class SAPHostExecVersion(CommandParser, LegacyItemAccess):
    """
    Class for parsing the output of `saphostexec -version` command.

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


    Attributes:
        components (dict): Dict of :py:class:`SAPComponent` instances.

    Examples:
        >>> type(sha_version)
        <class 'insights.parsers.saphostexec.SAPHostExecVersion'>
        >>> sha_version.components['saphostexec'].version
        '721'
        >>> sha_version.components['saphostexec'].patch
        '1011'
    """

    SAPComponent = namedtuple("SAPComponent",
            field_names=["version", "patch", "changelist"])
    """namedtuple: Type for storing the SAP components"""

    def parse_content(self, content):
        self.components = self.data = {}
        for line in content:
            # Only process component lines for now
            if not line.startswith('/usr/sap/hostctrl/exe/'):
                continue
            key, val = line.split(':', 1)
            key = key.split('/')[-1]
            ver, pch, chl, _ = [s.split()[-1].strip() for s in val.split(', ', 3)]
            self.components[key] = self.SAPComponent(ver, pch, chl)
