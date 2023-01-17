"""
DotNet- Comand ``/usr/bin/dotnet``
==================================

The parsers related ``/usr/bin/dotnet --version`` is included in this module.

DotNetVersion - command ``dotnet --version``
--------------------------------------------

ContainerDotNetVersion - command ``dotnet --version`` for containers
--------------------------------------------------------------------
"""
from insights.core import CommandParser, ContainerParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.dotnet_version)
class DotNetVersion(CommandParser):
    """
    Class for parsing the output of the ``/usr/bin/dotnet --version`` command.

    Sample output::

        3.1.108

    Examples:
        >>> dotnet_ver.major
        3
        >>> dotnet_ver.minor
        1
        >>> dotnet_ver.raw
        '3.1.108'
    """

    def parse_content(self, content):
        if not content or len(content) > 1:
            raise SkipComponent

        self.major = self.minor = None
        self.raw = content[0].strip()

        if ' ' not in self.raw and '.' in self.raw:
            v_sp = [i.strip() for i in self.raw.split('.', 2)]
            if len(v_sp) >= 2 and v_sp[0].isdigit() and v_sp[1].isdigit():
                self.major = int(v_sp[0])
                self.minor = int(v_sp[1])

        if self.major is None:
            raise ParseException("Unrecognized version: {0}", self.raw)


@parser(Specs.container_dotnet_version)
class ContainerDotNetVersion(ContainerParser, DotNetVersion):
    """
    Parses the output of the ``/usr/bin/dotnet --version`` command of the running
    containers which are based on RHEL images.

    Sample output::

        3.1.108

    Examples:
        >>> type(con_dotnet_ver)
        <class 'insights.parsers.dotnet.ContainerDotNetVersion'>
        >>> con_dotnet_ver.container_id
        'cc2883a1a369'
        >>> con_dotnet_ver.image
        'quay.io/rhel8'
        >>> con_dotnet_ver.engine
        'podman'
        >>> con_dotnet_ver.major
        3
        >>> con_dotnet_ver.minor
        1
        >>> con_dotnet_ver.raw
        '3.1.108'
    """

    pass
