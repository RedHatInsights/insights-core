"""
crontab - Command
=================

The classes in this module provide parsing for the ``crontab -l`` command.
The base class ``CrontabL`` provide all of the parsing logic and classes
that inherit are typically for a specific user, for example
``crontab -l -u some_user``.  Format of the output is the same regardless
of whether or not the `-u user` is specified.

Sample input looks like::

    # comment line
    * * * * * /usr/bin/keystone-manage token_flush > /dev/null 2>&1
    33 0 * * * /bin/heat-manage purge_deleted -g days 7

Each row of the crontab is converted into a dictionary with keys for each field.
For example one row would look like::

    {
      'minute': '*',
      'hour': '*',
      'day_of_month': '*',
      'month': '*',
      'day_of_week': '*',
      'command': '/usr/bin/keystone-manage token_flush > /dev/null 2>&1'
    }

Examples:
    >>> crontab = shared[KeystoneCrontab]
    >>> crontab.search('keystone')
    [{'minute': '*', 'hour': '*', 'day_of_month': '*', 'month': '*', 'day_of_week': '*',
      'command': '/usr/bin/keystone-manage token_flush > /dev/null 2>&1'}]
    >>> [r['minute'] for r in crontab]
    ['*', '33']
"""
from .. import Parser, parser, get_active_lines


class CrontabL(Parser):
    """Parses output of ``crontab -l`` command.

    Raises:
        AssertionError: Raised if a line is present in the input data that appears invalid.
    """
    def parse_content(self, content):
        self.data = []
        for line in get_active_lines(content):
            parts = line.split(None, 5)
            assert len(parts) == 6, "Crontab line appears corrupted, not enough parts: %r" % line
            row = {}
            row['minute'] = parts[0]
            row['hour'] = parts[1]
            row['day_of_month'] = parts[2]
            row['month'] = parts[3]
            row['day_of_week'] = parts[4]
            row['command'] = parts[5]
            self.data.append(row)

    def __iter__(self):
        for row in self.data:
            yield row

    def search(self, filter_str):
        """list: Returns list of dicts for lines that have `filter_str` in
        the command."""
        return [r for r in self.data if filter_str in r['command']]


@parser('heat_crontab')
class HeatCrontab(CrontabL):
    """Parses output of the ``crontab -l -u heat`` command."""
    pass


@parser('keystone_crontab')
class KeystoneCrontab(CrontabL):
    """Parses output of the ``crontab -l -u keystone`` command."""
    pass


@parser('root_crontab')
class RootCrontab(CrontabL):
    """Parses output of the ``crontab -l -u root`` command."""
    pass
