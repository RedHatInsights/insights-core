"""
openstack server list --all command - Command
=============================================
"""

from insights import CommandParser, parser, LegacyItemAccess
from insights.parsers import ParseException, SkipException, get_active_lines, parse_delimited_table
from insights.specs import Specs


@parser(Specs.openstack_server_list_all)
class OpenstackServerListAll(LegacyItemAccess, CommandParser):
    """
    This parser processes the output of the command `openstack server list --all` and provides
    the information as a list of dictionary.
    The LegacyItemAccess class provides some helper functions for dealing with a
    class having a `data` attribute.

    The output of command ``/usr/bin/openstack server list --all`` is in table format
        +--------------------------------------+--------------+--------+------------------------+----------------+------------+
        | ID                                   | Name         | Status | Networks               | Image          | Flavor     |
        +--------------------------------------+--------------+--------+------------------------+----------------+------------+
        | 410b05bb-59b7-4b4c-88e9-975c811d68da | compute-0    | ACTIVE | ctlplane=192.168.24.20 | overcloud-full | compute    |
        | f891e98b-4df6-4c90-9bf1-39cf8ac900b0 | compute-1    | ACTIVE | ctlplane=192.168.24.9  | overcloud-full | compute    |
        | 3d62cd7e-41d2-43dd-a5bf-5935bc319fae | controller-0 | ACTIVE | ctlplane=192.168.24.10 | overcloud-full | controller |
        +--------------------------------------+--------------+--------+------------------------+----------------+------------+

    Examples:
        >>> parser_result_server_list[2]['Flavor'] == 'controller'
        True
        >>> parser_result_server_list[0].get('Name')
        'compute-0'
        >>> parser_result_server_list[1]["Name"]
        'compute-1'
        >>> parser_result_server_list.get_list('ID')
        ['410b05bb-59b7-4b4c-88e9-975c811d68da', 'f891e98b-4df6-4c90-9bf1-39cf8ac900b0', '3d62cd7e-41d2-43dd-a5bf-5935bc319fae']
        >>> parser_result_server_list.get_startwith('Name','compute')
        ['compute-0', 'compute-1']
    """

    def parse_content(self, content):
        """
        Parse output content table of command ``/usr/bin/openstack server list --all``.
        Set each variable as an class attribute.
        """
        if not content:
            raise SkipException("Empty content.")
        if len(content) < 5:
            raise ParseException("Wrong content in table: '{0}'.".format(content))
        for _l in content:
            # Removes the lines starting with "+----"
            table = get_active_lines(content, comment_char='+')

            # Parses header line and each row using the "|" separator
            servers = parse_delimited_table(table, delim='|')
            for server in servers:
                if '' in server:
                    del server['']
            self.data = servers

    def get_list(self, key):
        '''
        returns the list of values for the specified key if the key exists
        returns ['', '', ''] if the key doesn't exist

        Example:
            >>> parser_result_server_list.get_list('Name')
            ['compute-0', 'compute-1', 'controller-0']
        '''
        list_ = [i.get(key, '') for i in self.data]
        self.list_ = list_
        return list_

    def get_startwith(self, key, startswith):
        '''
        returns the list of values that contains startswith

        Example:
            >>> parser_result_server_list.get_startwith('Name','compute')
            ['compute-0', 'compute-1']
        '''
        list_values = [i.get(key, '') for i in self.data]
        list_starts_with = [value for value in list_values if startswith in value]
        return list_starts_with
