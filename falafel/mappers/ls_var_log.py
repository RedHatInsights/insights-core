from .. import Mapper, mapper

from falafel.util.file_permissions import FilePermissions


# TODO - use FileListing? - https://gitlab.cee.redhat.com/insights-open-source/falafel/merge_requests/223

@mapper("ls_var_log")
class LsVarLog(Mapper):
    """
    A mapper for accessing "ls -laR /var/log". Read docstring for parse_content().
    """

    def __init__(self, *args, **kwargs):
        self.lines_unparsed = []
        self.dir_parsed = {}
        super(LsVarLog, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Parse "ls -laR /var/log" and save all the regular and link files in lists. The files and
        dirs are in the FilePermissions objects - the original line is available there as well as
        convenience methods. For each subdirectory, a separate list is created.

        Input Example:

        /var/log:
        total 1016
        drwxr-xr-x.  4 root root   4096 Oct 13 09:02 .
        drwxr-xr-x. 18 root root   4096 Jun 28 09:00 ..
        -rw-------.  1 root root  21504 Jun 28 09:00 anaconda.log
        drwxr-x---.  2 root root   4096 Jun 28 09:01 audit
        -rw-r--r--.  2 root root   1828 Oct 13 09:02 boot.log
        -rw-r--r--.  1 root root  21239 Oct 13 09:02 dmesg
        -rw-------.  1 root root  89840 Oct 14 09:40 messages

        /var/log/audit:
        total 132
        drwxr-x---. 2 root root   4096 Jun 28 09:01 .
        drwxr-xr-x. 4 root root   4096 Oct 13 09:02 ..
        -rw-------. 1 root root 121454 Oct 14 11:01 audit.log

        Output Example:

        {
            "/var/log":
                [
                    <FilePermissions object>,
                    <FilePermissions object>,
                    <FilePermissions object>,
                    <FilePermissions object>,
                    <FilePermissions object>,
                    <FilePermissions object>,
                    <FilePermissions object>,
                ],
            "/var/log/audit":
                [
                    <FilePermissions object>,
                    <FilePermissions object>,
                    <FilePermissions object>,
                ]
        }

        Args:
            content (context.content): Mapper context content
        """

        ls = {}
        self.lines_unparsed = []
        dir_name_title = ""  # if the ls output is malformed and there is no title with the dir name
        for line in content:
            self.lines_unparsed.append(line)
            if line.strip().endswith(":"):
                dir_name_title = line.split(":")[0]
            else:
                try:
                    file_permissions = FilePermissions(line)
                except ValueError:
                    # other lines than the files do not interest us
                    pass
                else:
                    if dir_name_title not in ls:
                        ls[dir_name_title] = []
                    ls[dir_name_title].append(file_permissions)
        self.dir_parsed = ls

    def get_filepermissions(self, dir_name_where_to_search, dir_or_file_name_to_get):
        """
        Returns the FilePermissions object, if found, for the specified dir or file name in the
        specified directory. The directory must be specified by the full path without trailing
        slash. The dir or file name to get must be specified by the name only (without path).

        Args:
            dir_name_where_to_search (string): Full path without trailing slash where to search.
            dir_or_file_name_to_getl (string): Name of the dir or file to get FilePermissions for.

        Returns:
            FilePermissions: If found or None if not found.
        """
        if dir_name_where_to_search in self.dir_parsed:
            for filePerm in self.dir_parsed[dir_name_where_to_search]:
                if filePerm.path == dir_or_file_name_to_get:
                    return filePerm
