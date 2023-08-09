"""
Sat6DBMigrateStatus - command ``foreman-rake db:migrate:status``
================================================================

This parser collects the output of the ``foreman-rake db:migrate:status``
command, which checks the status of all the migrations known to Foreman.
Each migration has a status, a date code, and a name.  These are stored
in a list of migrations, with 'up' migrations being listed in an ``up``
property and migrations with any other status being stored in a ``down``
property.

Sample input::

    database: foreman

     Status   Migration ID    Migration Name
    --------------------------------------------------
       up     20090714132448  Create hosts
       up     20090714132449  Add audits table
       up     20090715143858  Create architectures
       up     20090717025820  Create media
       up     20090718060746  Create domains
       up     20090718064254  Create subnets
       up     20090720134126  Create operatingsystems
       up     20090722140138  Create models

Examples:
    >>> status = shared[Sat6DBMigrateStatus]
    >>> status.database
    'foreman'
    >>> '20090714132448' in status.migrations
    True
    >>> '20090714140138' in status.migrations
    False
    >>> len(status.up)
    8
    >>> status.down
    []

"""
import re

from collections import namedtuple

from insights.core import CommandParser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


Migration = namedtuple("Migration", ('status', 'id', 'name'))
"""namedtuple: Stores one migration record"""


@parser(Specs.foreman_rake_db_migrate_status)
class Sat6DBMigrateStatus(CommandParser):
    """
    Parse the ``foreman-rake db:migrate:status`` command.

    Attributes:
        database (str): The name of the database (usually 'foreman')
        migrations (dict): All the migrations, indexed by migration ID.
        up (list): Only the 'up' migrations, in order of appearance
        down (list): All migrations not listed as 'up', in order of appearance
    """

    def parse_content(self, content):
        self.database = ''
        self.migrations = {}
        self.up = []
        self.down = []
        mig_re = re.compile(r'\s+(?P<status>\w+)\s+(?P<id>\d+)\s+(?P<name>\w.*)$')
        for line in content:
            if line.startswith('database: '):
                self.database = line[len('database: '):]
                continue
            match = mig_re.search(line)
            if match:
                migration = Migration(*match.group('status', 'id', 'name'))
                self.migrations[match.group('id')] = migration
                if match.group('status') == 'up':
                    self.up.append(migration)
                else:
                    self.down.append(migration)

        # Did we actually get a database and some lines?  If not there must
        # have been a parse error.
        if not (self.database and self.migrations):
            raise ParseException("Could not find database name nor any migrations")
