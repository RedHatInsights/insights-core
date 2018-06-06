"""
Lsof - command ``/usr/sbin/lsof``
=======================================

This parser reads the output of the ``/usr/sbin/lsof`` command and makes each
line available as a dictionary keyed on the fields in the lsof output (with
names in upper case).

Because of the large quantity of output from this command, this class is based
on the ``Scannable`` parser class.  There are several ways to use this:

* If you simply want to know whether a search matched, use the ``any`` method.
* If you want all lines that match, use the ``collect`` method.

The way these scanner functions work is:

1. You provide a function, which returns True if a match is found, and an
   attribute name.
2. The parser runs every scanner function across every line of data read and
   successfully parsed.
3. The attribute then contains the result of the match (True or False in the
   case of the ``any`` method, or the list of matching rows in the case of
   the ``collect`` method.

As an easier way of finding all the lines that match by key=value pairs, use
the ``collect_keys`` method, giving the name of the scanner attribute to set
and one or more 'key=value' pairs in the method call.  This then returns the
list of rows for which the data in all those keywords matched the respective
given values.  (**Note**: the ``SIZE/OFF`` column is searched for using the
key ``SIZE_OFF`` - see example below)

Sample output::

    COMMAND     PID  TID           USER   FD      TYPE             DEVICE  SIZE/OFF       NODE NAME
    systemd       1                root  cwd       DIR              253,1      4096        128 /
    systemd       1                root  rtd       DIR              253,1      4096        128 /
    systemd       1                root  txt       REG              253,1   1230920    1440410 /usr/lib/systemd/systemd
    systemd       1                root  mem       REG              253,1     37152  135529970 /usr/lib64/libnss_sss.so.2
    abrt-watc  8619                root    0r      CHR                1,3       0t0       4674 /dev/null
    wpa_suppl   641                root    0r      CHR                1,3       0t0       4674 /dev/null
    polkitd     642             polkitd    0u      CHR                1,3       0t0       4674 /dev/null
    polkitd     642             polkitd    1u      CHR                1,3       0t0       4674 /dev/null

Examples:

    >>> Lsof.any('systemd_commands', lambda x: 'systemd' in x['COMMAND'])
    >>> Lsof.collect('polkitd_user', lambda x: x['USER'] == 'polkitd')
    >>> Lsof.collect_keys('root_stdin', USER='root', FD='0r', SIZE_OFF='0t0')
    >>> l = shared[Lsof]
    >>> l.systemd_commands
    True
    >>> len(l.polkitd_user)
    2
    >>> l.polkitd_user[0]['DEVICE']
    '1,3'
    >>> len(l.root_stdin)
    2
    >>> l.root_stdin[0]['COMMAND']
    'abrt-watc'

"""

from .. import add_filter, Scannable, parser, CommandParser
from insights.specs import Specs

add_filter(Specs.lsof, ['COMMAND'])


@parser(Specs.lsof)
class Lsof(CommandParser, Scannable):
    """
    A parser for the output of ``/usr/sbin/lsof`` - determines the column
    widths from the first row and then puts the data in each row into a
    dictionary keyed on the column name and found by the locations of each
    column.  Leading and trailing spaces are stripped from data.
    """

    def _calc_indexes(self, line):
        self.header_row = line
        self.name_idx = self.header_row.index(" NAME")
        self.pid_idx = self.header_row.index("  PID")
        _, self.mid_cols = self.header_row[:self.name_idx].split(None, 1)
        self.mid_cols = "  " + self.mid_cols
        self.indexes = {}
        for col_name in self.mid_cols.split():
            self.indexes[col_name] = self.mid_cols.index(col_name) + len(col_name)
        self.indexes["FD"] += 2

    def _split_middle(self, middle):
        mid_dict = {}
        offset = 0
        for col in self.mid_cols.split():
            idx = self.indexes[col]
            mid_dict[col] = middle[offset:idx].strip()
            offset = idx
        return mid_dict

    def _start(self, content):
        """
        Consumes lines from content until the HEADER is found and processed.
        Returns an iterator over the remaining lines.
        """
        content = iter(content)

        line = next(content)
        while 'COMMAND ' not in line:
            line = next(content)

        self._calc_indexes(line)
        return content

    def _parse_line(self, line):
        """
        Given a line, returns a dictionary for that line. Requires _start to be
        called first.
        """
        command, rest = line[:self.pid_idx], line[self.pid_idx:]
        name = line[self.name_idx:]
        middle_dict = self._split_middle(rest[:self.name_idx - len(command)])
        middle_dict["COMMAND"] = command.strip()
        middle_dict["NAME"] = name.strip()
        return middle_dict

    def parse(self, content):
        """
        Parse the content for the entire input file.
        """
        for line in self._start(content):
            yield self._parse_line(line)

    @classmethod
    def collect_keys(cls, result_key, **kwargs):
        """
        Store a list of lines having keyword=value matches in the given
        attribute name.

        Keyword argument names that exist as column names in the data are
        searched for in the lines of the file and stored in the ``result_key``
        attribute.  All columns must match (i.e. this is a bolean AND search).

        Call this class method before using the class data.

        Examples:
            collect_keys('root_block_devs', USER='root', TYPE='BLK')
        """
        def scanner(self, obj):
            # Have to set the attribute so it exists, even if it has no rows
            if not hasattr(self, result_key):
                setattr(self, result_key, [])
            # Minor hack - search for 'SIZE/OFF' as 'SIZE_OFF'.
            if 'SIZE_OFF' in kwargs:
                kwargs['SIZE/OFF'] = kwargs['SIZE_OFF']
            # Filter the keywords for the list of column names requested.
            for key in [k for k in kwargs if k in obj]:
                # If we have a keyword whose value doesn't match the given
                # item, then skip out now.
                if obj[key] != kwargs[key]:
                    return
            # OK, save the item now.
            getattr(self, result_key).append(obj)

        cls._scan(result_key, scanner)
