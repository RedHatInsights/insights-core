"""
mpirun Version - Command
========================

The parser for ``mpirun --version`` is included in this module.

"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.mpirun_version)
class MPIrunVersion(CommandParser):
    """
    Class for parsing the output of the ``/usr/local/bin/mpirun --version`` command.

    Sample output::

        Intel(R) MPI Library for Linux* OS, Version 2019 Update 12 Build 202010429 (id: e380127cb)
        Copyright 2003-2021, Intel Corporation.

    Examples:
        >>> mpirun_ver.year
        '2019'
        >>> mpirun_ver.version
        'Version 2019 Update 08 Build 202010429 (id: e380127cb)'
    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty content.")
        if len(content) != 2:
            raise SkipComponent("Content not parsable.")

        self.year = content[0].split('Version ')[1].split(" ")[0]
        self.version = content[0].split(', ')[-1]
