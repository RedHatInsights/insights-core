"""
mpirun Version - Command
========================

The parser for ``mpirun --version`` is included in this module.

"""
from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.mpirun_version)
class MPIrun(CommandParser):
    """
    Class for parsing the output of the ``/usr/bin/mpirun --version`` command.

    Sample output::

        Intel(R) MPI Library for Linux* OS, Version 2019 Update 12 Build 202010429 (id: e380127cb)
        Copyright 2003-2021, Intel Corporation.

    mpirun versions list launched according to years:
    openmpi-3.1.0 to openmpi-3.1.3 -> 2018
    openmpi-3.1.4 to openmpi-3.1.6 -> 2019
    openmpi-4.0.0 to openmpi-4.1.0 -> 2020
    openmpi-4.1.1 to openmpi-4.1.2 -> 2021
    openmpi-5.0.0 - continue_to_release -> 2022

    Examples:
        >>> mpirun_ver.year
        2019
        >>> mpirun_ver.version
        'Version 2019 Update 08 Build 202010429 (id: e380127cb)'
    """
    def parse_content(self, content):
        if not content or len(content) > 2:
            raise SkipException

        self.year = int(content[0].split('Version ')[1].split(" ")[0])
        self.version = content[0].split(', ')[1]
