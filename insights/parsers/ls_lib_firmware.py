"""
Lists ALL the firmware packages
===============================

Parsers included in this module are:

LsLibFW - command ``/bin/ls -lARkhvX /lib/firmware``
----------------------------------------------------

"""

from .. import LogFileOutput, parser, CommandParser, get_active_lines
from insights.specs import Specs
import re

@parser(Specs.ls_lib_fw)
class LsLibFW(CommandParser):
    """
    This parser will help to parse the output of command ``/bin/ls -lARkhvX /lib/firmware``

    Typical output of the ``/bin/ls -lARkhvX /lib/firmware`` command is::
	
        /lib/firmware/:
	total 53M
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 3com
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 acenic
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 adaptec
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 advansys
	drwxr-xr-x.  2 root root 4.0K Jul  3 06:53 amd-ucode
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 av7110
	drwxr-xr-x.  2 root root 4.0K Jul  3 06:53 b43-open
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 bnx2
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 bnx2x
	drwxr-xr-x.  2 root root 4.0K Jul  3 07:29 brcm
	
	/lib/firmware/av7110:
	total 4.0K
	-rw-r--r--. 1 root root 212 May 24 18:46 bootcode.bin
	
	/lib/firmware/b43-open:
	total 20K
	-rw-r--r--. 1 root root  158 Mar 19  2015 b0g0bsinitvals5.fw
	-rw-r--r--. 1 root root  976 Mar 19  2015 b0g0initvals5.fw
	-rw-r--r--. 1 root root 9.4K Mar 19  2015 ucode5.fw
	
	/lib/firmware/bnx2:
	total 924K
	-rw-r--r--. 1 root root  93K May 24 18:46 bnx2-mips-06-5.0.0.j6.fw
	-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.0.15.fw
	-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.2.1.fw
	-rw-r--r--. 1 root root  91K May 24 18:46 bnx2-mips-06-6.2.3.fw
	
	/lib/firmware/bnx2x:
	total 8.0M
	-rw-r--r--. 1 root root 149K May 24 18:46 bnx2x-e1-6.2.5.0.fw
	-rw-r--r--. 1 root root 149K May 24 18:46 bnx2x-e1-6.2.9.0.fw
	-rw-r--r--. 1 root root 158K May 24 18:46 bnx2x-e1-7.0.20.0.fw
	-rw-r--r--. 1 root root 158K May 24 18:46 bnx2x-e1-7.0.23.0.fw 

    Example:

        >>> 
        >>> 

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
            line = re.sub(' +',' ', line)
            if line.startswith("/lib/firmware"):
                dir_name = line.split(":")[0]
                self.data[dir_name] = {}
            elif line.startswith("total"):
                self.data[dir_name]['total']= line.split(" ")[1]
            else:
                line = line.split(" ")
                if len(line) == 11:
                    file_name = ' '.join(line[8:11])
                    self.data[dir_name][file_name] = line[0:8]
                if len(line) == 9:
                    file_name = line[8]
                    self.data[dir_name][file_name] = line[0:8]


    def check_file_present(self, fpath):
        dir_path, file_path = self.sep_dir_file(fpath)
        return True if ((dir_path in self.data) and (file_path in self.data[dir_path])) else False

    
    def get_file_details(self, fpath):
        if self.check_file_present(fpath):
            dir_path, file_path = self.sep_dir_file(fpath)
            return self.data[dir_path][file_path]
