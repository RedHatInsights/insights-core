"""
Disk Usage parsers
==================

Module for the processing of output from the ``du`` command.

Parsers provided by this module include:

DiskUsageDir - command ``du -s -k {directory}``
-----------------------------------------------

"""
from insights import parser, CommandParser
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


class DiskUsage(CommandParser, dict):
    """
    Reads output of du command and turns it into a dictionary with pathname as
    key and size in blocks.

    Supports parsing input data as long as output is 2 column data with first
    column as space size with integer values only and second as pathname which
    can be a file or directory. Space size with decimal values or unit suffixes
    like M, GiB is not supported.

    du command produces output in 1K blocks unless block size is specified in
    command options or an environment variable. This parser is intended to be
    used only with default block size of 1K which is also equal to plain "du"
    or "du -k".

    Sample input data::

        56	/var/lib/alternatives
        4	/var/lib/logrotate
        5492	/var/lib/mlocate
        20	/var/lib/NetworkManager
        186484	/var/lib/pgsql
        856	/var/lib/rhsm
        110712	/var/lib/rpm
        4	/var/lib/rsyslog
        64	/var/lib/systemd
        15200	/var/lib/yum

    Examples:
        >>> '/var/lib/pgsql' in disk_usage
        True
        >>> disk_usage.get('/var/lib/pgsql')
        186484
        >>> int(disk_usage.get('/var/lib/pgsql') / 1024) # to MiB
        182

    Raises:
        SkipException: When no data could be parsed.
        ParseException: Raised when any problem parsing the command output.
    """

    def parse_content(self, content):
        """
        Parse input data into a dictionary.
        """
        # For errors like :
        # /bin/du: cannot read directory '/somepath'
        # /bin/du: cannot access `/somepath': No such file or directory
        du_error = 'bin/du: '

        for line in content:
            if du_error in line:
                continue

            line_split = line.split(None, 1)
            if len(line_split) != 2:
                raise ParseException("Could not parse line: {0}".format(line))
            size, path = line_split
            path = path.rstrip()
            if path.startswith('.'):
                raise ParseException("Relative paths not supported: {0}'".
                                     format(line))
            if path and size.isdigit():
                self[path] = int(size)
            else:
                raise ParseException("Could not parse line: '{0}'".
                                     format(line))
        if len(self) == 0:
            raise SkipException('No data parsed')


@parser(Specs.du_dirs)
class DiskUsageDir(DiskUsage):
    """
    Parser class for processing du output for multiple directories, each
    collected using ``du -s -k {directory}``.
    """
    pass
