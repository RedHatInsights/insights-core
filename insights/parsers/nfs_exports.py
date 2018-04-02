"""
NFS exports configuration
=========================

NFSExports and NFSExportsD provide a parsed output of the content of an exports
file as defined in ``man exports(5)``.  The content is parsed into a
dictionary, where the key is the export path and the value is another
dictionary, where the key is the hostname and the value is the option list,
parsed into an actual list.

The default (``"-"``) hostname is not specially handled, nor are wildcards.

If export paths are defined multiple times in a file, only the first one is
parsed.  All subsequent redefinitions are not parsed and the raw line is added
to the ``ignored_lines`` member.

All raw lines are kept in ``raw_lines``, which is a ``dict`` where the key is
the export path and the value is the stripped raw line.

Parsers included in this module are:

NFSExports - file ``nfs_exports``
---------------------------------

NFSExportsD - files in the ``nfs_exports.d`` directory
------------------------------------------------------

Sample input is shown in the Examples.

Examples:
    >>> EXPORTS='''
    ... /home/utcs/shared/ro @rht(ro,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
    ... /home/insights/shared/rw @rht(rw,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(ro,sync,no_root_squash)
    ... /home/insights/shared/special/all/mail   @rht(rw,sync,no_root_squash)
    ... /home/insights/ins/special/all/config   @rht(ro,sync,no_root_squash)  ins1.example.com(rw,sync,no_root_squash)
    ... #/home/insights ins1.example.com(rw,sync,no_root_squash)
    ... /home/example           @rht(rw,sync,root_squash) ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
    ... /home/example           ins3.example.com(rw,sync,no_root_squash)
    ... '''
    >>> print json.dumps(nfs_exports.data, indent=4)
    {
        "/home/insights/shared/rw": {
            "@rht": [
                "rw",
                "sync"
            ],
            "ins1.example.com": [
                "rw",
                "sync",
                "no_root_squash"
            ],
            "ins2.example.com": [
                "ro",
                "sync",
                "no_root_squash"
            ]
        },
        "/home/insights/ins/special/all/config": {
            "@rht": [
                "ro",
                "sync",
                "no_root_squash"
            ],
            "ins1.example.com": [
                "rw",
                "sync",
                "no_root_squash"
            ]
        },
        "/home/insights/shared/special/all/mail": {
            "@rht": [
                "rw",
                "sync",
                "no_root_squash"
            ]
        },
        "/home/example": {
            "@rht": [
                "rw",
                "sync",
                "root_squash"
            ],
            "ins1.example.com": [
                "rw",
                "sync",
                "no_root_squash"
            ],
            "ins2.example.com": [
                "rw",
                "sync",
                "no_root_squash"
            ]
        },
        "/home/utcs/shared/ro": {
            "@rht": [
                "ro",
                "sync"
            ],
            "ins1.example.com": [
                "rw",
                "sync",
                "no_root_squash"
            ],
            "ins2.example.com": [
                "rw",
                "sync",
                "no_root_squash"
            ]
        }
    }
    >>> nfs_exports.ignored_lines
    ['/home/example           ins3.example.com(rw,sync,no_root_squash)']
    >>> nfs_exports.all_options()
    set(['ro', 'no_root_squash', 'rw', 'sync', 'root_squash'])
    >>> nfs_exports.export_paths()
    set(['/home/insights/shared/rw', '/home/insights/ins/special/all/config', '/home/insights/shared/special/all/mail', '/home/example', '/home/utcs/shared/ro'])
"""

from itertools import chain
from .. import Parser, parser
from . import get_active_lines


class NFSExportsBase(Parser):
    """
    Class to parse ``/etc/exports`` and ``/etc/exports.d/*.exports``.

    Attributes:
        data (dict): Key is export path, value is a dict, where the key is the
            client host and the value is a list of options.

        ignored_lines (list): List of lines that are not used by ``nfsd``.

        raw_lines (dict): Key is export path, value is raw line (though it is
            transformed via ``get_active_lines``)
    """

    def _parse_host(self, content):
        if "(" in content:
            host, options = content.split("(")
            options = options.rstrip(")").split(",")
        else:
            host, options = content, []
        return host, options

    def _parse_line(self, line):
        split = [i.strip() for i in line.split()]
        path, hosts = split[0], dict(self._parse_host(s) for s in split[1:])
        return path, hosts

    def parse_content(self, content):
        # Reversing order of lines because only the first line for a given path
        # is parsed; all others are ignored.  Thus reversing enables us to
        # utilize dict overrides.
        active_lines = get_active_lines(content)
        line_gen = (self._parse_line(l) for l in reversed(active_lines))
        self.data = {path: hosts for path, hosts in line_gen}
        self.ignored_lines = list(self._find_ignored_lines(active_lines))
        self.raw_lines = {l.split()[0]: l for l in active_lines}

    @staticmethod
    def _find_ignored_lines(lines):
        """
        Only the first line for a given export path is used; all others are
        ignored
        """
        seen_paths = set()
        for line in lines:
            path = line.split()[0]
            if path in seen_paths:
                yield line
            else:
                seen_paths.add(path)

    def export_paths(self):
        """Returns the set of all export paths as strings"""
        return set(self.data.keys())

    def all_options(self):
        """Returns the set of all options used in all export entries"""
        items = chain.from_iterable(hosts.values() for hosts in self.data.values())
        return set(chain.from_iterable(items))

    def __iter__(self):
        return self.data.iteritems()

    @staticmethod
    def reconstitute(path, d):
        """
        Reconstruct a line from its parsed value.  Original whitespace is not
        maintained; instead two spaces (``"  "``) is used between each word.

        Args:
            path (str): The export path
            d (dict): The dictionary that's the value of the exported path key
                      in the parsed dict.

        Returns:
            str: The reconstituted line from the exports file
        """
        return "  ".join([path] + ["%s(%s)" % (host, ",".join(options))
                         for host, options in d.iteritems()])


@parser('nfs_exports')
class NFSExports(NFSExportsBase):
    """Subclass to attach ``nfs_exports`` spec to"""
    pass


@parser('nfs_exports.d')
class NFSExportsD(NFSExportsBase):
    """Subclass to attach ``nfs_exports.d`` spec to"""
    pass
