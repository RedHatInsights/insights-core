from insights import parser, CommandParser
from insights.parsers import get_active_lines, ParseException

import re
from insights.specs import Specs


def _make_cron_re():
    """
    Make the regular expression that matches a crontab 'cron' line.

    Each field has a set of allowed values, and can then be in a range, and be
    listed with dashes.  A range can be stepped with the '/' modifier, and
    ranges can be in a list.  A field can also be '*', or '*' divided in steps.

    The best way to do this is to have a template for a single field that
    encapsulates the syntax of that field, regardless of what that field
    matches.  We then fill in the actual template's value with the pattern
    that matches that field.  Each field is named, so we can pull them out as
    a dictionary later.
    """
    range_ = r"{val}(?:-{val}(?:/\d+)?)?"
    template = r"(?P<{name}>" + "(?:\*(?:/\d+)?|{r}(?:,{r})*)".format(r=range_) + ")\s+"
    return (
        r'^\s*' +
        template.format(name='minute', val=r'(?:\d|[012345]\d)') +
        template.format(name='hour', val=r'(?:\d|[01]\d|2[0123])') +
        template.format(name='day_of_month', val=r'(?:0?[1-9]|[12]\d|3[01])') +
        template.format(name='month', val=r'(?:0?[1-9]|1[012]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)') +
        template.format(name='day_of_week', val=r'(?:[0-7]|mon|tue|wed|thur|fri|sat|sun)') +
        r'(?P<command>\S.*)$'
    )


class CrontabL(CommandParser):
    """
    Parses output of ``crontab -l`` command.

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

    Crontab parses the line in the same way that cron(1) does.  Lines that
    are blank or start with a comment are ignored.  Environment lines of the
    form 'KEY = value' (with optional spacing around the equals sign) are
    stored in the 'environment' dictionary attribute by key.  Lines
    containing a valid crontab line, with five recogniseable time fields and
    a command, are stored in the `data` property and accessed through the
    pseudo-list interface and search method.  All other lines are stored in
    the `invalid_lines` property.

    Crontab recognises the extension of time signature 'nicknames', which
    take place of the first five parts of a standard crontab line:

        * `@reboot` : Run once after reboot.
        * `@yearly` : Run once a year, ie.  "0 0 1 1 \*".
        * `@annually` : Run once a year, ie.  "0 0 1 1 \*".
        * `@monthly` : Run once a month, ie. "0 0 1 \* \*".
        * `@weekly` : Run once a week, ie.  "0 0 \* \* 0".
        * `@daily` : Run once a day, ie.   "0 0 \* \* \*".
        * `@hourly` : Run once an hour, ie. "0 \* \* \* \*".

    The Crontab class recognises these nicknames.  In the case of the '@reboot'
    nickname, the row will not contain the 'minute', 'hour', 'day_of_month',
    'month', or 'day_of_week' keys, and instead will contain the key 'time' with
    the value '@reboot' (as well as the usual 'command' key).  All other keywords
    are translated directly into their five-part equivalent and parsed as a normal
    crontab line.

    Lines that can't be parsed because they don't contain at least six words or
    meet the criteria for environment line or time signature nicknames are stored
    in the ``invalid_lines`` property.

    Sample input looks like::

        # send mail to admin address.
        MAILTO=admin
        * * * * * /usr/bin/keystone-manage token_flush > /dev/null 2>&1
        33 0 * * * /bin/heat-manage purge_deleted -g days 7

    Examples:
        >>> crontab = shared[KeystoneCrontab]
        >>> crontab.search('keystone')
        [{'minute': '*', 'hour': '*', 'day_of_month': '*', 'month': '*', 'day_of_week': '*',
          'command': '/usr/bin/keystone-manage token_flush > /dev/null 2>&1'}]
        >>> [r['minute'] for r in crontab]
        ['*', '33']
        >>> crontab.invalid_lines
        []
        >>> len(crontab)  # Number of actual entries
        2
        >>> crontab[0]  # Individual entry access
        {'minute': '*', 'hour': '*', 'day_of_month': '*', 'month': '*', 'day_of_week': '*',
          'command': '/usr/bin/keystone-manage token_flush > /dev/null 2>&1'}
        >>> 'MAILTO' in crontab.environment  # Dictionary of environment settings
        True
        >>> crontab.environment['MAILTO']
        'admin'

    Attributes:

        data(list): List of parsed lines.  These can be accessed directly through
            the object as seen in the examples.
        environment(dict): A dictionary of environment declarations in the crontab.
        invalid_lines(list): Lines that could not be parsed as normal crontab
            entries.
    """
    def parse_content(self, content):
        self.data = []
        self.environment = {}
        self.invalid_lines = []
        # Crontabs can use 'nicknames' for common event frequencies:
        nicknames = {
            '@yearly': '0 0 1 1 *',
            '@annually': '0 0 1 1 *',
            '@monthly': '0 0 1 * *',
            '@weekly': '0 0 * * 0',
            '@daily': '0 0 * * *',
            '@hourly': '0 * * * *',
        }
        cron_re = re.compile(_make_cron_re(), flags=re.IGNORECASE)
        env_re = re.compile(r'^\s*(?P<key>\w+)\s*=\s*(?P<value>\S.*)$')
        for line in get_active_lines(content):
            if line.startswith('@'):
                # Reboot is 'special':
                if line.startswith('@reboot'):
                    parts = line.split(None, 2)
                    self.data.append({'time': '@reboot', 'command': parts[1]})
                    continue
                else:
                    parts = line.split(None, 2)
                    if parts[0] not in nicknames:
                        raise ParseException(
                            "{n} not recognised as a time specification 'nickname'".format(n=parts[0])
                        )
                    # Otherwise, put the time spec nickname translation into
                    # the line
                    line = line.replace(parts[0], nicknames[parts[0]])
                    # And then we fall through to the rest of the parsing.
            cron_match = cron_re.match(line)
            env_match = env_re.match(line)
            if cron_match:
                self.data.append(cron_match.groupdict())
            elif env_match:
                # Environment variable - capture in dictionary
                self.environment[env_match.group('key')] = env_match.group('value')
            else:
                self.invalid_lines.append(line)

    def __getitem__(self, idx):
        """
        Get the n'th item from the crontab table.

        Arguments:
            idx(int): The index of the crontab line, starting from 0.

        Returns:
            (dict): the number of items
        """
        return self.data[idx]

    def __iter__(self):
        """
        Iterates through the list of crontab entries.

        Yields:
            (dict): The next parsed crontab entry.
        """
        for row in self.data:
            yield row

    def search(self, filter_str):
        """list: Returns list of dicts for lines that have `filter_str` in
        the command."""
        return [r for r in self.data if filter_str in r['command']]


@parser(Specs.heat_crontab)
class HeatCrontab(CrontabL):
    """Parses output of the ``crontab -l -u heat`` command."""
    pass


@parser(Specs.keystone_crontab)
class KeystoneCrontab(CrontabL):
    """Parses output of the ``crontab -l -u keystone`` command."""
    pass


@parser(Specs.nova_crontab)
class NovaCrontab(CrontabL):
    """Parses output of the ``crontab -l -u nova`` command."""
    pass


@parser(Specs.root_crontab)
class RootCrontab(CrontabL):
    """Parses output of the ``crontab -l -u root`` command."""
    pass
