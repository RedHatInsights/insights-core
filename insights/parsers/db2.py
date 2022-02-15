"""
DB2 commands
============

Shared parsers for parsing output of the commands of IBM DB2

Db2ls - command ``db2ls -a -c``
-------------------------------
"""
from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.db2ls_a_c)
class Db2ls(CommandParser, list):
    """
    Parse the output of `db2ls -a -c` into a list of dictionaries.

    Typical output of this command::

        #PATH:VRMF:FIXPACK:SPECIAL:INSTALLTIME:INSTALLERUID
        /opt/ibm/db2/V11.5:11.5.6.0:0 ::Fri Jan 14 20:20:07 2022 CST :0
        /opt/ibm/db2/V11.5_01:11.5.7.0:0 ::Fri Feb 11 10:34:51 2022 CST :0

    Examples:
        >>> type(db2ls)
        <class 'insights.parsers.db2.Db2ls'>
        >>> len(db2ls)
        2
        >>> db2ls[0]['PATH']
        '/opt/ibm/db2/V11.5'
        >>> db2ls[1]['PATH']
        '/opt/ibm/db2/V11.5_01'
        >>> db2ls[1]['VRMF']
        '11.5.7.0'
        >>> db2ls[1]['INSTALLERUID']
        '0'
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty.")
        keys = []
        for line in content:
            if not keys and line.startswith('#PATH'):
                keys = [i.strip('#') for i in line.split(':')]
                continue
            line_splits = [i.strip() for i in line.split(':', 4)]
            line_splits.extend([i.strip(': ') for i in line_splits.pop(-1).rsplit(':', 1)])
            self.append(dict(zip(keys, line_splits)))
        if len(self) == 0:
            raise SkipException('Nothing to parse.')
