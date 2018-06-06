"""
DockerInfo - Comand ``/usr/bin/docker info``
============================================

This parser reads the output of ``/usr/bin/docker info``.

The resulting data structure is avaible in the ``data`` member of the class
and takes the form of a dictionary whose keys are the "keys" in the output
(the string before the ``:``) and whose values are the values (the string
following the ``:``), all stripped of leading and trailing spaces.

Sample output::

    Containers: 0
    Images: 0
    Server Version: 1.9.1
    Storage Driver: devicemapper
    Pool Name: rhel-docker--pool
    Pool Blocksize: 524.3 kB
    Base Device Size: 107.4 GB
    Backing Filesystem: xfs
    Data file:
    Metadata file:
    Data Space Used: 62.39 MB
    Data Space Total: 3.876 GB
    Data Space Available: 3.813 GB
    Metadata Space Used: 40.96 kB
    Metadata Space Total: 8.389 MB
    Metadata Space Available: 8.348 MB
    Udev Sync Supported: true
    Deferred Removal Enabled: true
    Deferred Deletion Enabled: true
    Deferred Deleted Device Count: 0
    Library Version: 1.02.107-RHEL7 (2015-12-01)
    Execution Driver: native-0.2
    Logging Driver: json-file
    Kernel Version: 3.10.0-327.el7.x86_64
    CPUs: 1
    Total Memory: 993 MiB
    Name: host001.example.com
    ID: QPOX:46K6:RZK5:GPBT:DEUD:QM6H:5LRE:R63D:42DI:4BH3:6ZOZ:5EUM

Examples:

    >>> docker_info = shared[DockerInfo]
    >>> docker_info.data['Containers']
    '0'
    >>> docker_info.data['ID']
    'QPOX:46K6:RZK5:GPBT:DEUD:QM6H:5LRE:R63D:42DI:4BH3:6ZOZ:5EUM'

If the command does not return the information (for example, the Docker
daemon isn't running, the ``data`` dictionary is empty.

"""

from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.docker_info)
class DockerInfo(CommandParser):
    """
    Represents the output of the ``/usr/bin/docker info`` command.

    The resulting output of the command is essentially key/value pairs.
    """

    def parse_content(self, content):
        self.data = {}
        # there will be more than 10 lines in the command output if "docker info"
        # command executes successfully.
        if len(content) >= 10:
            for line in content:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    value = value.strip()
                    value = value if value else None
                    self.data[key.strip()] = value
