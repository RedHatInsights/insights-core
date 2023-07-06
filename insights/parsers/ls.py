"""
LS Parsers - command ``ls``
===========================

Parsers provided in this module includes:

LSla - command ``ls -la <dirs>``
--------------------------------

LSlaFiltered - command ``ls -la <dirs> | grep -F <keywords>``
-------------------------------------------------------------

LSlan - command ``ls -lan <dirs>``
----------------------------------

LSlanFiltered - command ``ls -lan <dirs> | grep -F <keywords>``
---------------------------------------------------------------

LSlanL - command ``ls -lanL <dirs>``
------------------------------------

LSlanR - command ``ls -lanR <dirs>``
------------------------------------

LSlanRL - command ``ls -lanRL <dirs>``
--------------------------------------

LSlanRZ - command ``ls -lanRZ <dirs>``
--------------------------------------

LSlanZ - command ``ls -lanZ <dirs>``
------------------------------------
"""
from insights.core import ls_parser, Parser
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util.file_permissions import FilePermissions

add_filter(Specs.ls_la_filtered, ['total '])
add_filter(Specs.ls_lan_filtered, ['total '])


class FileListing(Parser, dict):
    """
    Reads a series of concatenated directory listings and turns them into
    a dictionary of entities by name.  Stores all the information for
    each directory entry for every entry that can be parsed, containing::

        - type (one of [bcdlps-])
        - permission string including ACL character
        - number of links
        - owner and group (as given in the listing)
        - size, or major and minor number for block and character devices
        - date (in the format given in the listing)
        - name
        - name of linked file, if a symlink

    In addition, the raw line is always stored, even if the line doesn't look
    like a directory entry.

    Also provides a number of other conveniences, such as::

        - lists of regular and special files and subdirectory names for each
          directory, in the order found in the listing
        - total blocks allocated to all the entities in this directory

    Parses the SELinux information if present in the listing.
    SELinux directory listings contain::

        - the type of file
        - the permissions block
        - the owner and group as given in the directory listing
        - the SELinux user, role, type and MLS
        - the name, and link destination if it's a symlink

    .. note::
        The :class:`FileListing` Parser parses the content collected by
        diffirent ``ls_*`` specs. The ``ls_*`` specs collect the corresponding
        ``ls`` command output according to the filters defined by the relevant
        ``ls_*_dirs`` specs.  For the ``ls_*_dirs`` specs, only absolute
        directory path is acceptable, path to file or relative path is not
        acceptable.  For details, see the following example.

    Sample output::

        /boot:
        total 187380
        dr-xr-xr-x.  3 0 0   4096 Mar  4 16:19 .
        dr-xr-xr-x. 19 0 0   4096 Jul 14 09:10 ..
        -rw-r--r--.  1 0 0 123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64

        /etc/sysconfig:
        total 96
        drwxr-xr-x.  7 0 0 4096 Jul  6 23:41 .
        drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..
        drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
        drwxr-xr-x.  2 0 0    6 Sep 16  2015 console
        -rw-------.  1 0 0 1390 Mar  4  2014 ebtables-config
        -rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld
        lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub

    Examples:
        >>> from insights.core.filters import add_filter
        >>> from insights.specs import Specs
        >>> add_filter(Specs.ls_lan_dirs, ['/boot', '/etc/sysconfig'])
        >>> type(ls_lan)
        <class 'insights.parsers.ls.FileListing'>
        >>> "/etc" in ls_lan
        False
        >>> "/etc/sysconfig" in ls_lan
        True
        >>> len(ls_lan.files_of('/etc/sysconfig'))
        3
        >>> ls_lan.files_of("/etc/sysconfig")
        ['ebtables-config', 'firewalld', 'grub']
        >>> ls_lan.dirs_of("/etc/sysconfig")
        ['.', '..', 'cbq', 'console']
        >>> ls_lan.specials_of("/etc/sysconfig")
        []
        >>> ls_lan.total_of("/etc/sysconfig")
        96
        >>> ls_lan.dir_entry('/etc/sysconfig', 'grub') == {'group': '0', 'name': 'grub', 'links': 1, 'perms': 'rwxrwxrwx.', 'raw_entry': 'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub', 'owner': '0', 'link': '/etc/default/grub', 'date': 'Jul  6 23:32', 'type': 'l', 'dir': '/etc/sysconfig', 'size': 17}
        True
        >>> sorted(ls_lan.listing_of("/etc/sysconfig").keys()) == sorted(['console', 'grub', '..', 'firewalld', '.', 'cbq', 'ebtables-config'])
        True
        >>> sorted(ls_lan.listing_of("/etc/sysconfig")['console'].keys()) == sorted(['group', 'name', 'links', 'perms', 'raw_entry', 'owner', 'date', 'type', 'dir', 'size'])
        True
        >>> ls_lan.listing_of("/etc/sysconfig")['console']['type']
        'd'
        >>> ls_lan.listing_of("/etc/sysconfig")['console']['perms']
        'rwxr-xr-x.'
        >>> ls_lan.dir_contains("/etc/sysconfig", "console")
        True
        >>> ls_lan.dir_entry("/etc/sysconfig", "console") == {'group': '0', 'name': 'console', 'links': 2, 'perms': 'rwxr-xr-x.', 'raw_entry': 'drwxr-xr-x.  2 0 0    6 Sep 16  2015 console', 'owner': '0', 'date': 'Sep 16  2015', 'type': 'd', 'dir': '/etc/sysconfig', 'size': 6}
        True
        >>> ls_lan.dir_entry("/etc/sysconfig", "grub")['type']
        'l'
        >>> ls_lan.dir_entry("/etc/sysconfig", "grub")['link']
        '/etc/default/grub'
        >>> "/boot" in ls_lan
        True
        >>> ls_lan.files_of('/boot')
        ['config-3.10.0-229.14.1.el7.x86_64']
        >>> fp = ls_lan.permissions_of('/boot', 'config-3.10.0-229.14.1.el7.x86_64')
        >>> fp.owner
        '0'
        >>> fp.group
        '0'
        >>> fp.perms_owner
        'rw-'
    """
    def parse_content(self, content):
        """
        Called automatically to process the directory listing(s) contained in
        the content.
        """
        self.update(ls_parser.parse(content))

    def files_of(self, directory):
        """
        The list of non-special files (i.e. not block or character files)
        in the given directory.
        """
        if directory in self:
            return self[directory]['files']
        return []

    def dirs_of(self, directory):
        """
        The list of subdirectories in the given directory.
        """
        if directory in self:
            return self[directory]['dirs']
        return []

    def specials_of(self, directory):
        """
        The list of block and character special files in the given directory.
        """
        if directory in self:
            return self[directory]['specials']
        return []

    def total_of(self, directory):
        """
        The total blocks of storage consumed by entries in this directory.
        """
        if directory in self:
            return self[directory]['total']
        return 0

    def listing_of(self, directory):
        """
        The listing of this directory, in a dictionary by entry name.  All
        entries contain the original line as is in the 'raw_entry' key.
        Entries that can be parsed then have fields as described in the class
        description above.
        """
        if directory in self:
            return self[directory]['entries']
        return []

    def dir_contains(self, directory, name):
        """
        Does this directory contain this entry name?
        """
        if directory in self:
            return name in self[directory]['entries']
        return False

    def dir_entry(self, directory, name):
        """
        The parsed data for the given entry name in the given directory.
        """
        if directory in self:
            return self[directory]['entries'][name]
        return {}

    def path_entry(self, path):
        """
        The parsed data given a path, which is separated into its directory
        and entry name.
        """
        if path[0] != '/':
            return None
        path_parts = path.split('/')
        # Note that here the first element will be '' because it's before the
        # first separator.  That's OK, the join puts it back together.
        directory = '/'.join(path_parts[:-1])
        if directory not in self:
            return None
        name = path_parts[-1]
        if name not in self[directory]['entries']:
            return None
        return self[directory]['entries'][name]

    def permissions_of(self, directory, target):
        """
        Returns a FilePermissions object, if found.

        Parameters:
            directory(string): Full path without trailing slash where to
                search.
            target (string): Name of the directory or file to get
                FilePermissions for.

        Returns:
            FilePermissions: If found or None if not found.
        """
        if directory in self:
            d = self[directory]['entries']
            if target in d:
                return FilePermissions(d[target]['raw_entry'])


@parser(Specs.ls_la)
class LSla(FileListing):
    """
    Parses output of ``ls -la <dirs>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_la_filtered)
class LSlaFiltered(FileListing):
    """
    Parses output of ``ls -la <dirs> | grep -F <keywords>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_lan)
class LSlan(FileListing):
    """
    Parses output of ``ls -lan <dirs>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_lan_filtered)
class LSlanFiltered(FileListing):
    """
    Parses output of ``ls -lan <dirs> | grep -F <keywords>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_lanL)
class LSlanL(FileListing):
    """
    Parses output of ``ls -lanR <dirs>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_lanR)
class LSlanR(FileListing):
    """
    Parses output of ``ls -lanR <dirs>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_lanRL)
class LSlanRL(FileListing):
    """
    Parses output of ``ls -lanRL <dirs>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_lanRZ)
class LSlanRZ(FileListing):
    """
    Parses output of ``ls -lanRZ <dirs>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass


@parser(Specs.ls_lanZ)
class LSlanZ(FileListing):
    """
    Parses output of ``ls -lanZ <dirs>`` command.
    See :py:class:`FileListing` for more information.
    """
    pass
