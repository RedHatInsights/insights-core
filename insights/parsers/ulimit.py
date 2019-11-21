"""
Ulimit - Command ``ulimit -a -H`` and ``ulimit -a -S``
======================================================
Parses the output of the `ulimit -a -S` and `ulimit -a -S` command:

Parsers included in this module are:

UlimitHard - Command ``ulimit -a -H``
-------------------------------------

UlimitSoft - Command ``ulimit -a -S``
-------------------------------------
"""

from collections import namedtuple
from insights import CommandParser, parser
from insights.parsers import SkipException
from insights.specs import Specs

Ulimit = namedtuple("Ulimit", field_names=["name", "details", "limits_value"])
"""namedtuple: Type for storing the specific ulimit line."""

class UlimitBase(CommandParser, dict):
    """
    Base class for `ulimit -a` command. The parsing result can be accessed like
    a dict in which the key are the resource name with spaces replaced to "_".

    Sample data::

        stack size              (kbytes, -s) 30720
        core file size          (blocks, -c) unlimited
        pending signals                 (-i) 15063
        max locked memory       (kbytes, -l) 64
        max memory size         (kbytes, -m) unlimited
        open files                      (-n) 4096

    Parsing Result::

        {
            'core_file_size': Ulimit(name='core_file_size', details=['blocks', '-c'], limits_value='unlimited'),
            'max_locked_memory': Ulimit(name='max_locked_memory', details=['kbytes', '-l'], limits_value=64),
            'max_memory_size': Ulimit(name='max_memory_size', details=['kbytes', '-m'], limits_value='unlimited'),
            'open_files': Ulimit(name='open_files', details=['-n'], limits_value=4096),
            'pending_signals': Ulimit(name='pending_signals', details=['-i'], limits_value=15063),
            'stack_size': Ulimit(name='stack_size', details=['kbytes', '-s'], limits_value=30720)
        }

    Raises:
        SkipException: When nothing needs to parse.

    """

    def parse_content(self, content):
        if not content:
            raise SkipException()

        for line in content:
            line_sp = line.split('(')
            name = line_sp[0].strip().replace(" ", "_")
            line_sp = line_sp[1].split(')')
            details = [i.strip() for i in line_sp[0].split(",")]
            limits_value = line_sp[1].strip()
            if limits_value.isdigit():
                limits_value = int(limits_value)

            self[name] = Ulimit(name, details, limits_value)

        if len(self) == 0:
            raise SkipException()

    def data(self):
        """ To keep backward compitable. """
        return self


@parser(Specs.ulimit_hard)
class UlimitHard(UlimitBase):
    """
    Class to parse the command `ulimit -a -H`. For details, refer to the base
    class :class:`UlimitBase`

    Examples:
        >>> ulimit_hard['stack_size'].limits_value
        30720
        >>> ulimit_hard['open_files'].name == 'open_files'
        True
        >>> 'blocks' in ulimit_hard['core_file_size'].details
        True
    """
    pass



@parser(Specs.ulimit_soft)
class UlimitSoft(UlimitBase):
    """
    Class to parse the command `ulimit -a -S`. For details, refer to the base
    class :class:`UlimitBase`

    Examples:
        >>> ulimit_soft['stack_size'].limits_value
        30720
        >>> ulimit_soft['open_files'].name == 'open_files'
        True
        >>> 'blocks' in ulimit_soft['core_file_size'].details
        True
    """
    pass
