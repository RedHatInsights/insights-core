"""
Lists ALL the firmware packages
===============================

Parsers included in this module are:

LsLibFW - command ``/bin/ls -lARkhvX /lib/firmware``
----------------------------------------------------

"""

import re

from insights.specs import Specs

from .. import parser, CommandParser, get_active_lines


@parser(Specs.ls_lib_fw)
class LsLibFW(CommandParser):
    """
    This parser will help to parse the output of command ``/bin/ls -lARkhvX /lib/firmware``

    Typical output of the ``/bin/ls -lARkhvX /lib/firmware`` command is::

    \t/lib/firmware/:
    \ttotal 53M
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 3com
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 acenic
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 adaptec
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 advansys
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 06:53 amd-ucode
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 av7110
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 06:53 b43-open
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 bnx2
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 bnx2x
    \tdrwxr-xr-x.  2 root root 4.0K Jul  3 07:29 brcm
    \t
    \t/lib/firmware/av7110:
    \ttotal 4.0K
    \t-rw-r--r--. 1 root root 212 May 24 18:46 bootcode.bin
    \t
    \t/lib/firmware/b43-open:
    \ttotal 20K
    \t-rw-r--r--. 1 root root  158 Mar 19  2015 b0g0bsinitvals5.fw
    \t-rw-r--r--. 1 root root  976 Mar 19  2015 b0g0initvals5.fw
    \t-rw-r--r--. 1 root root 9.4K Mar 19  2015 ucode5.fw
    \t
    \t/lib/firmware/bnx2:
    \ttotal 924K
    \t-rw-r--r--. 1 root root  93K May 24 18:46 bnx2-mips-06-5.0.0.j6.fw
    \t-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.0.15.fw
    \t-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.2.1.fw
    \t-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.2.3.fw
    \t
    \t/lib/firmware/bnx2x:
    \ttotal 8.0M
    \t-rw-r--r--. 1 root root 149K May 24 18:46 bnx2x-e1-6.2.5.0.fw
    \t-rw-r--r--. 1 root root 149K May 24 18:46 bnx2x-e1-6.2.9.0.fw
    \t-rw-r--r--. 1 root root 158K May 24 18:46 bnx2x-e1-7.0.20.0.fw
    \t-rw-r--r--. 1 root root 158K May 24 18:46 bnx2x-e1-7.0.23.0.fw

    Example:

        >>> type(lslibfw)
        <class 'insights.parsers.ls_lib_firmware.LsLibFW'>
        >>> lslibfw.path_exist("/lib/firmware/bnx2x/")
        True
        >>> lslibfw.path_exist("/lib/firmware/bnx2x/bnx2x-e1-6.2.9.0.fw")
        True
        >>> lslibfw.get_file_details("/lib/firmware/bnx2/bnx2-mips-06-6.2.1.fw")
        ['-rw-r--r--.', '1', 'root', 'root', '91K', 'May', '24', '18:46']

    """

    def __init__(self, *args, **kwargs):
        self.data = {}
        """dict: Dictionary of firmware package details"""
        super(LsLibFW, self).__init__(*args, **kwargs)

    def sep_dir_file(self, fpath):
        dir_path = fpath.split('/')
        file_path = dir_path.pop()
        dir_path = '/'.join(dir_path)
        return dir_path, file_path

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content
        """
        for line in get_active_lines(content):
            line = re.sub(' +', ' ', line)
            if line.startswith("/lib/firmware"):
                dir_name = line.split(":")[0]
                self.data[dir_name] = {}
            elif line.startswith("total"):
                self.data[dir_name]['total'] = line.split(" ")[1]
            else:
                line = line.split(" ")
                if len(line) == 11:
                    file_name = ' '.join(line[8:11])
                    self.data[dir_name][file_name] = line[0:8]
                if len(line) == 9:
                    file_name = line[8]
                    self.data[dir_name][file_name] = line[0:8]

    def path_exist(self, fpath):
        """
        This parser method is to confirm if firmware package is exists in the path

        Args:
            Firmware package dir/file path (Directory path should end with /)

        Returns:
            (bool): It will return `True` if package is present in the path, `False` when absent.
        """
        dir_path, file_path = self.sep_dir_file(fpath)
        if dir_path and file_path:
            return True if ((dir_path in self.data) and (file_path in self.data[dir_path])) else False
        elif dir_path and not file_path:
            return True if (dir_path in self.data) else False
        elif not dir_path and file_path:
            return True if (file_path in self.data) else False

    def get_file_details(self, fpath):
        """
        This parser method is to get the firmware file details

        Args:
            Firmware package file path

        Returns:
            (list): It will return `list` of file permissions, user, group, size, time if file is present
                    in the path. It will return `None` when file not present in the path.
        """
        if self.path_exist(fpath):
            dir_path, file_path = self.sep_dir_file(fpath)
            if dir_path and file_path:
                return self.data[dir_path][file_path]
