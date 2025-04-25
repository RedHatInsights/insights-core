"""
ls_target_files - parser for datasource ls_files output
=======================================================

Classes to parse the output of datasource ls_files:


LsTargetFiles - /usr/bin/ls <file path>
---------------------------------------
"""
from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.smartctl_health)
class LsTargetFiles(JSONParser):
    """
    Parse the output of command "/usr/bin/ls <file path>".

    Sample input::

        {
            "/dev/sdb2": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/sdb2",
            "/dev/mapper/rhel-root": "brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/mapper/rhel-root"
        }

    Examples:
        >>> type(ls_target_files_info)
        <class 'insights.parsers.ls_target_files.LsTargetFiles'>
        >>> ls_target_files_info.data["/dev/sdb2"]
        'brw-rw----. 1 0 6 252, 1 Apr 25 03:47 /dev/sdb2'

    """
    pass
