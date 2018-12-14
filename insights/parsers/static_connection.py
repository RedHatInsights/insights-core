"""
StaticConnectionShow - files ``/usr/bin/nmcli connection show``
===============================================================

This file will parse the output of all the nmcli connections.

Sample configuration from a teamed interface in file ``/usr/bin/nmcli connection show``::

  NAME      UUID                                  TYPE      DEVICE 
  enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3 
  virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0 
  test-net  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --

Examples:

    >>> STATIC_CONNECTION_SHOW = '''
    ... NAME      UUID                                  TYPE      DEVICE 
    ... enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3 
    ... virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0 
    ... test-net  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --
    ... '''.strip()
    >>> static_conn = StaticConnectionShow(context_wrap(STATIC_CONNECTION_SHOW))
    >>> assert static_conn.get_disconnected_connection == ["test-net"]
    >>> assert static_conn[2]['NAME'] == "test-net"
"""
from insights import parser, CommandParser
from insights.parsers import parse_delimited_table
from insights.specs import Specs


@parser(Specs.nmcli_conn_status)
class StaticConnectionShow(CommandParser):
    def parse_content(self, content):
        self.data = parse_delimited_table(content)
        self.disconnected_connection = []

    @property
    def get_disconnected_connection(self):
        for all_connection in self.data:
            if all_connection['NAME'] != all_connection['DEVICE']:
                self.disconnected_connection.append(all_connection['NAME'])

        return self.disconnected_connection

    def __getitem__(self, idx):
        return self.data[idx]
