"""
LS Parsers - command ``ls <Specific File>``
===========================================

Parsers provided in this module includes:

LSla - command ``ls -lad <dirs>``
---------------------------------
"""
from insights.core import ls_parser, Parser
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util.file_permissions import FilePermissions
from insights.core.exceptions import SkipComponent

# Required basic filters for `LS` specs that the content needs to be filtered


class SpecificFileListing(Parser, dict):
    """
    Parses output of ``ls <specific file list>`` command.
    The list of specific file is returned from datasource.

    Sample output::

        ls: cannot access 'swap': No such file or directory
        dr-xr-xr-x. 21 root root 4096 Oct 15 08:19 /
        drwxr-xr-x.  2 root root    6 Nov  9  2021 /boot

    Examples:
        >>> type(ls_specific_file)
        <class 'insights.parsers.ls_specific_file.LSladSpecificFile'>
        >>> '/' in ls_specific_file
        True
        >>> ls_specific_file.get('/').get('owner')
        'root'
        >>> ls_specific_file.get('/boot').get('perms')
        'rwxr-xr-x.'
    """
    __root_path = None

    def parse_content(self, content):
        """
        Called automatically to process the directory listing(s) contained in
        the content.
        """
        parsed_content = []
        for line in content:
            if 'No such file or directory' not in line:
                parsed_content.append(line)
        if not parsed_content:
            raise SkipComponent
        ls_data = ls_parser.parse(parsed_content, '').get('')
        self.update(ls_data.get('entries'))


@parser(Specs.ls_lad_specific_file)
class LSladSpecificFile(SpecificFileListing):
    """
    Parses output of ``ls -la <dirs>`` command.
    See :py:class:`SpecificFileListing` for more information.
    """
    pass
