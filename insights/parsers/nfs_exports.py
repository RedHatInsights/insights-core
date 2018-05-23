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

Sample content of the ``/etc/exports`` file::

    /home/utcs/shared/ro                    @group(ro,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
    /home/insights/shared/rw                @group(rw,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(ro,sync,no_root_squash)
    /home/insights/shared/special/all/mail  @group(rw,sync,no_root_squash)
    /home/insights/ins/special/all/config   @group(ro,sync,no_root_squash)  ins1.example.com(rw,sync,no_root_squash)
    #/home/insights                          ins1.example.com(rw,sync,no_root_squash)
    /home/example                           @group(rw,sync,root_squash) ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)
    # A duplicate host for this exported path
    /home/example                           ins2.example.com(rw,sync,no_root_squash)

Examples:
    >>> type(exports)
    <class 'insights.parsers.nfs_exports.NFSExports'>
    >>> type(exports.data) == type({})
    True
    >>> exports.raw_lines['/home/insights/shared/rw']  # List of lines that define this path
    ['/home/insights/shared/rw                @group(rw,sync)   ins1.example.com(rw,sync,no_root_squash) ins2.example.com(ro,sync,no_root_squash)']
    >>> exports.raw_lines['/home/example']  # Lines are stored even if they contain duplicate hosts
    ['/home/example                           @group(rw,sync,root_squash) ins1.example.com(rw,sync,no_root_squash) ins2.example.com(rw,sync,no_root_squash)', '/home/example                           ins2.example.com(rw,sync,no_root_squash)']
    >>> exports.ignored_exports
    {'/home/example': {'ins2.example.com': ['rw', 'sync', 'no_root_squash']}}
    >>> sorted(list(exports.all_options()))
    ['no_root_squash', 'ro', 'root_squash', 'rw', 'sync']
    >>> sorted(list(exports.export_paths()))
    ['/home/example', '/home/insights/ins/special/all/config', '/home/insights/shared/rw', '/home/insights/shared/special/all/mail', '/home/utcs/shared/ro']
"""

from itertools import chain

from .. import Parser, parser
from . import get_active_lines
from insights.specs import Specs
from insights.util import deprecated


class NFSExportsBase(Parser):
    """
    Class to parse ``/etc/exports`` and ``/etc/exports.d/*.exports``.

    Exports are stored keyed on the path of the export, and then the host
    definition.  The flags are stored as a list.  NFS allows the same path
    to be listed on multiple lines and in multiple files, but an exported
    path can only have one definition for a given host.

    Attributes:
        data (dict): Key is export path, value is a dict, where the key is the
            client host and the value is a list of options.

        ignored_exports (dict): A dictionary of exported paths that have host
            definitions that conflicted with a previous definition.

        ignored_lines (dict): A synonym for the above `ignored_exports`
            dictionary, for historical reasons.

        raw_lines (dict of lists): The list of the raw lines that define each
            exported path, including any lines that may have ignored exports.
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
        # Exports can be duplicated, but the path-host tuple cannot: the
        # first read will be stored and all later path-host tuples cause
        # `exportfs` to generate a warning when setting up the export.
        self.data = {}
        self.ignored_exports = {}
        self.ignored_lines = self.ignored_exports
        self.raw_lines = {}

        for line in get_active_lines(content):
            path, hosts = self._parse_line(line)
            if path not in self.data:
                # New path, just add the hosts.
                self.data[path] = hosts
                self.raw_lines[path] = [line]
            else:
                # Add to raw lines even if some (or all) hosts are ignored.
                self.raw_lines[path].append(line)
                # Have to check each path-host tuple
                for host, flags in hosts.items():
                    if host not in self.data[path]:
                        # Only add if it doesn't already exist.
                        self.data[path][host] = flags
                    else:
                        if path not in self.ignored_exports:
                            self.ignored_exports[path] = {host: flags}
                        else:
                            self.ignored_exports[path][host] = flags

    def export_paths(self):
        """Returns the set of all export paths as strings"""
        return set(self.data.keys())

    def all_options(self):
        """Returns the set of all options used in all export entries"""
        items = chain.from_iterable(hosts.values() for hosts in self.data.values())
        return set(chain.from_iterable(items))

    def __iter__(self):
        return iter(self.data.items())

    @staticmethod
    def reconstitute(path, d):
        """
        'Reconstitute' a line from its parsed value.  The original lines are
        not used for this.  The hosts in d are listed in alphabetical order,
        and the options are listed in the order originally given.

        This function is deprecated.  Please use the `raw_lines` dictionary
        property of the parser instance instead, as this contains the actual
        lines from the exports file.

        Arguments:
            path (str): The exported path
            d (dict): The hosts definition of the exported path

        Returns:
            str: A line simulating the definition of that exported path to
            those hosts.
        """
        deprecated(
            NFSExportsBase.reconstitute,
            'Please use the `raw_lines` dictionary property of the parser instance'
        )
        return "  ".join([path] + ["%s(%s)" % (host, ",".join(options))
                         for host, options in d.items()])


@parser(Specs.nfs_exports)
class NFSExports(NFSExportsBase):
    """Subclass to attach ``nfs_exports`` spec to"""
    pass


@parser(Specs.nfs_exports_d)
class NFSExportsD(NFSExportsBase):
    """Subclass to attach ``nfs_exports.d`` spec to"""
    pass
