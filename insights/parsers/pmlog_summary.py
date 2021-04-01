"""
PmLogSummary - Command ``pmlogsummary``
=======================================
"""

from insights import parser, CommandParser
from insights.parsers import SkipComponent
from insights.specs import Specs


def parse(data):
    """
    Parse a set of key/value pairs into a heirarchical dictionary of
    typed values

    Arguments:
        data (dict): Input dictionary of key/value pairs

    Returns:
        dict: Heirarchical dictionary with keys separated at "." and type
        conversion of the numerical values
    """
    result = {}

    def typed(x):
        try:
            return float(x)
        except Exception:
            return x

    def insert(k, v):
        cur = result
        key_parts = k.split(".")

        # walk down the structure to the correct leaf
        for part in key_parts:
            if part not in cur:
                cur[part] = {}
            cur = cur[part]

        # break the value apart and store it
        l, r = v.split(None, 1)
        cur["val"] = typed(l)
        cur["units"] = r.strip()

    def kvs():
        # deal with whitespace and high level splitting
        for line in data:
            line = line.strip()
            if line:
                yield line.split(None, 1)

    for k, v in kvs():
        insert(k, v)

    return result


@parser(Specs.pmlog_summary)
class PmLogSummary(CommandParser, dict):
    """
    Parser to parse the output of the ``pmlogsummary`` command

    Sample output of the command is::

        mem.util.used  3133919.812 Kbyte
        mem.physmem  3997600.000 Kbyte
        kernel.all.cpu.user  0.003 none
        kernel.all.cpu.sys  0.004 none
        kernel.all.cpu.nice  0.000 none
        kernel.all.cpu.steal  0.000 none
        kernel.all.cpu.idle  3.986 none
        disk.all.total  0.252 count / sec

    Output is parsed and stored as a dictionary.  Each value is
    stored as a dict in the form ``{'val': number or string, 'units': string}``.
    Keys are a hierarchy of the input key value split on the "." character.
    For instance input line "mem.util.used  3133919.812 Kbyte" is parsed
    as::

        {
            'mem': {
                'util': {
                    'used': {
                        'val': 3133919.812,
                        'units': 'Kbyte'
                    }
                }
            }
        }

    Example:
        >>> type(pmlog_summary)
        <class 'insights.parsers.pmlog_summary.PmLogSummary'>
        >>> 'mem' in pmlog_summary
        True
        >>> pmlog_summary['disk']['all']['total'] == {'val': 0.252, 'units': 'count / sec'}
        True
    """

    def parse_content(self, content):
        data = parse(content)

        if len(data) == 0:
            raise SkipComponent()

        self.update(data)
