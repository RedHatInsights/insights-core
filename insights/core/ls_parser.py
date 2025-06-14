"""
This module contains logic for parsing ls output. It attempts to handle
output when selinux is enabled or disabled and also skip "bad" lines.
"""

import re


def trim_fname(fname):
    """
    Remove enclosing quotes or double quotes in file name.
    """
    # Fastest way seems to be compare to set first, then compare first and last
    if fname[0] in {'"', "'"} and fname[0] == fname[-1]:
        return fname[1:-1]
    return fname


def set_name_link(entry, is_softlink, path):
    """
    Get the name, and possibly the link, from the rest of the path.

    Args:
        entry (dict): the dict to put this data into
        is_softlink (bool): is this actually a softlink?
        path (str): the rest of the line, optionally including the link

    Returns:
        Does not return, entry keys for name and link added
    """
    if is_softlink:
        name, _, link = path.partition(" -> ")
        entry['name'] = trim_fname(name)
        entry['link'] = trim_fname(link)
    else:
        entry['name'] = trim_fname(path)


def parse_major_minor_date(last, result):
    """
    Parse the size / major, minor and date section of the line.

    Args:
        last (str): the rest of the line after the owner and group.
        result (dict): the dirent dict to put details in.

    Returns:
        The file name portion of the line.
    """
    # device numbers only go to 256.
    # If a comma is in the first four characters, the next two elements are
    # major and minor device numbers. Otherwise, the next element is the size.
    if "," in last[:4]:
        major, minor, rest = last.split(None, 2)
        result["major"] = int(major.rstrip(","))
        result["minor"] = int(minor)
    else:
        size, rest = last.split(None, 1)
        result["size"] = size if size == '?' else int(size)
    # The date part is always 12 characters regardless of content.
    result['date'] = rest[:12]
    return rest[13:]


def parse_non_selinux(entry, is_softlink, links, owner, group, last):
    """
    Parse part of an ls output line that isn't selinux.

    Args:
        entry (dict): the dict to put this data into
        is_softlink (bool): is this actually a softlink?
        links (str): the number of links on this dirent
        owner (str): the owner (name or id) of this dirent
        group (str): the group (name or id) of this dirent
        last (str): the rest of the line

    Returns:
        A dict containing links, owner, group, date, and name. If the line
        represented a device, major and minor numbers are included.  Otherwise,
        size is included. If the raw name was a symbolic link, link is
        included.
    """
    # prw-------.  1 0 0   0 Jun 28 09:44 5.ref
    # l??????????  ? ? ?    ?            ? invocation:auditd.service

    entry["links"] = links if links == '?' else int(links)
    entry["owner"] = owner
    entry["group"] = group

    rest = parse_major_minor_date(last, entry)

    set_name_link(entry, is_softlink, rest)


def set_selinux(entry, selinux_str):
    """
    Set the SELinux part of this entry
    """
    selinux = selinux_str.split(":")
    lsel = len(selinux)
    entry["se_user"] = selinux[0]
    entry["se_role"] = selinux[1] if lsel > 1 else None
    entry["se_type"] = selinux[2] if lsel > 2 else None
    entry["se_mls"] = selinux[3] if lsel > 3 else None


def parse_old_selinux(entry, is_softlink, owner, group, selinux_str, name_part):
    """
    Parse part of an ls output line that is selinux.

    Args:
        entry (dict): the dict to put this data into
        is_softlink (bool): is this actually a softlink?
        links (str): the number of links on this dirent
        owner (str): the owner (name or id) of this dirent
        group (str): the group (name or id) of this dirent
        selinux_str (str): the SELinux context of this dirent
        name_part (str): the name (and possibly link))

    Returns:
        No return; the ownership, SELinux context information and name part
        are put directly into the entry dict.

    """

    entry["owner"] = owner
    entry["group"] = group
    set_selinux(entry, selinux_str)
    set_name_link(entry, is_softlink, name_part)


def parse_rhel8_selinux(entry, is_softlink, links, owner, group, last):
    """
    Parse part of an ls output line that is selinux on RHEL8.

    Args:
        entry (dict): the dict to put this data into
        is_softlink (bool): is this actually a softlink?
        links (str): the number of links on this dirent
        owner (str): the owner (name or id) of this dirent
        group (str): the group (name or id) of this dirent
        last (str): the rest of the line

    Returns:
        No return; the ownership, SELinux context information and name part
        are put directly into the entry dict.

    """
    entry["links"] = int(links) if links.isdigit() else links
    entry["owner"] = owner
    entry["group"] = group
    selinux_str, last = last.split(None, 1)
    set_selinux(entry, selinux_str)
    rest = parse_major_minor_date(last, entry)
    set_name_link(entry, is_softlink, rest)


parse_mode = {
    'normal': parse_non_selinux,
    'selinux': parse_old_selinux,
    'rhel8_selinux': parse_rhel8_selinux
}


class Directory(dict):
    def __init__(self, dirname, total, body):
        dirs = []
        ents = {}
        files = []
        specials = []
        parser = None
        for line in body:
            # we can't split(None, 5) here b/c rhel 6/7 selinux lines only have
            # 4 parts before the path, and the path itself could contain
            # spaces. Unfortunately, this means we have to split the line again
            # below
            try:
                perms, links, owner, group, rest = line.split(None, 4)
            except ValueError:
                # Ignore malformed lines completely
                continue
            typ = perms[0]
            entry = {
                "type": typ,
                "perms": perms[1:],
                "dir": dirname,
            }
            # determine mode once per directory
            if parser is None:
                if links[0].isdigit():
                    # We have to split the line again to see if this is a RHEL8
                    # selinux stanza. This assumes that the context section will
                    # always have at least two pieces separated by ':'.
                    # '?' as the whole RHEL8 security context is also acceptable.
                    # Handle normal case first...
                    if rest[0].isdigit():
                        # crw-------.  1 0 0 10,  236 Jul 25 10:00 control
                        # lrwxrwxrwx.  1 0 0       11 Aug  4  2014 menu.lst -> ./grub.conf
                        parser = parse_mode['normal']
                    else:
                        # -rwxrwxr-x. 1 user group unconfined_u:object_r:var_lib_t:s0 54 Apr  8 16:41 abcd-efgh-ijkl-mnop
                        parser = parse_mode['rhel8_selinux']
                else:
                    # -rw-r--r--. root root system_u:object_r:boot_t:s0      config-3.10.0-267
                    parser = parse_mode['selinux']
            # Now parse based on mode
            parser(entry, typ == 'l', links, owner, group, rest)

            # final details
            # entry["raw_entry"] = line

            nm = entry["name"]
            ents[nm] = entry
            # Files are most common, dirs next, so we handle this in frequency order
            if typ in "-l":
                files.append(nm)
            elif typ == "d":
                dirs.append(nm)
            else:
                specials.append(nm)

        super(Directory, self).__init__(
            {
                "dirs": dirs,
                "entries": ents,
                "files": files,
                "name": dirname,
                "specials": specials,
                "total": total,
            }
        )


def parse(lines, root=None):
    """
    Parses a list of lines from ls into dictionaries representing their
    components.

    Args:
        lines (list): A list of lines generated by ls.
        root (str): The directory name to be used for ls output stanzas that
            don't have a name.

    Returns:
        A dictionary representing the ls output. It's keyed by the path
        containing each ls stanza.
    """
    doc = {}
    entries = []
    name = None
    total = None
    for line in lines:
        line = line.strip()
        # Skip empty line and non-exist dir line
        if not line or ': No such file or directory' in line or 'cannot open directory' in line:
            continue
        if line[0] == "/" and line[-1] == ":":
            # Directory name - like '/tmp:'
            if total is None:
                total = len(entries)
            # Some old directory listings don't have an initial name line,
            # so we put any entries we collected before a named directory in
            # our 'root' directory - if we got a 'root' directory at all...
            old_name = root if name is None else name
            if old_name is not None:
                doc[old_name] = Directory(old_name, total, entries)
            name = line[:-1]
            total = None
            entries = []
            continue
        if line.startswith("total"):
            # Should be first line after directory name
            total = int(line[6:])
            continue
        entries.append(line)
    name = name or root
    total = total if total is not None else len(entries)
    doc[name] = Directory(name, total, entries)
    return doc


class FilePermissions(object):
    """
    Class for parsing `ls -l` line targeted at concrete file and handling parsed properties.

    It is useful for checking file permissions and owner.

    Attributes:
        type (str): The type indicator (d, c, b, l or -)
        perms_owner (str): Owner permissions, e.g. 'rwx'
        perms_group (str): Group permissions
        perms_other (str): Other permissions
        owner (str): Owner user name
        group (str): Owner group name
        path (str): Full path to file

    Note:
        This class does not support Access Control Lists (ACLs). If that is needed in the future,
        it would be preferable to create another class than extend this one.
        Advanced File Permissions - SUID, SGID and Sticky Bit - are not yet correctly parsed.
    """

    _PERMISSIONS_PATTERN = re.compile(
        r'''
        ^
        (.)([-rwxsStT]{3})([-rwxsStT]{3})([-rwxsStT]{3})   # -rwxrwxrwx
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        # ^^^^^^^^^^
        # Valid characters are -rwxsStT
        #   s == setuid/setgid
        #   S == setuid/setgid without execute permissions
        #   t == sticky bit
        #   T == sticky bit without execute bit

        \S*                      # the character(s) after rwxrwxrwx for ACLs/xattrs
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #           ^

        \s+\S+\s+                # the number of hardlinks and spaces around
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #            ^^^

        ([^\s:]+)\s+([^\s:]+)    # owner, spaces, group
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #               ^^^^^^^^^
        # Username and group name are strings without whitespace \s and without colon :.

        \s+(?:\d+|\d+,\s*\d+)+\s+        # (size or major/minor) and spaces around
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #                        ^^^^^^
        # brw-rw----. 1 root disk 252, 1 May 16 01:30 /dev/vda1
        #                        ^^^^^^^^

        \S+\s+\S+                # month and day
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #                              ^^^^^^

        \s+\S+\s+                # time/year and spaces around
        # -rw-------. 1 root root 4308 Apr 22 2009 /etc/ssh/sshd_config
        #                                    ^^^^^^
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #                                    ^^^^^^^

        (.*)                     # file name or path
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #                                           ^^^^^^^^^^^^^^^^^^^^
        # -rw-------. 1 root root 4308 Apr 22 15:57 file_name_without_path
        #                                           ^^^^^^^^^^^^^^^^^^^^^^

        $
        ''',
        re.VERBOSE,
    )

    def __init__(self, line):
        """
        Args:
            line (str): A line from `ls -l /concrete/file` execution. Such as:
                        -rw-------. 1 root root 762 Sep 23 002 /etc/ssh/sshd_config
                        -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
                        -rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub2/grub.cfg
                        brw-rw----. 1 root disk 252, 1 May 16 01:30 /dev/vda1
        Raises:
            ValueError: If line is malformed
        """
        self.line = line
        r = self._PERMISSIONS_PATTERN.search(self.line)
        if r:
            (
                self.type,
                self.perms_owner,
                self.perms_group,
                self.perms_other,
                self.owner,
                self.group,
                self.path,
            ) = r.groups()
            parts = self.line.split()
            if "," in parts[4]:
                self.major = int(parts[4].strip(","))
                self.minor = int(parts[5])
            else:
                self.size = int(parts[4])
        else:
            raise ValueError('Invalid `ls -l` line "{}"'.format(self.line))

    @classmethod
    def from_dict(cls, dirent):
        """
        Create a new FilePermissions object from the given dictionary.  This
        works with the FileListing parser class, which has already done the
        hard work of pulling many of these fields out.  We create an object
        with all the dictionary keys available as properties, and also split
        the ``perms`` string up into owner, group
        """
        # Get a new instance without having to provide a line.
        self = cls.__new__(cls)
        # Check that we have at least as much data as the __init__ requires
        for k in ['type', 'perms', 'owner', 'group', 'name', 'dir']:
            if k not in dirent:
                raise ValueError("Need required key '{k}'".format(k=k))
        # Copy all values across
        for key, val in dirent.items():
            setattr(self, key, val)
        # Fill in names that might not have been passed from the ls parser
        self.path = self.name
        # Create perms parts
        self.perms_owner = self.perms[0:3]
        self.perms_group = self.perms[3:6]
        self.perms_other = self.perms[6:9]
        return self

    def owned_by(self, owner, also_check_group=False):
        """
        Checks if the specified user or user and group own the file.

        Args:
            owner (str): the user (or group) name for which we ask about ownership
            also_check_group (bool): if set to True, both user owner and group owner checked
                                if set to False, only user owner checked

        Returns:
            bool: True if owner of the file is the specified owner
        """
        if also_check_group:
            return self.owner == owner and self.group == owner
        else:
            return self.owner == owner

    def owner_can_read(self):
        """
        Checks if owner can read the file. Write and execute bits are not evaluated.

        Returns:
            bool: True if owner can read the file.
        """
        return 'r' in self.perms_owner

    def group_can_read(self):
        """
        Checks if group can read the file. Write and execute bits are not evaluated.

        Returns:
            bool: True if group can read the file.
        """
        return 'r' in self.perms_group

    def others_can_read(self):
        """
        Checks if 'others' can read the file. Write and execute bits are not evaluated. ('others' in
        the sense of unix permissions that know about user, group, others.)

        Returns:
            bool: True if 'others' can read the file.
        """
        return 'r' in self.perms_other

    def owner_can_only_read(self):
        """
        Checks if owner has read-only permissions for the file.
        Therefore, write and execute bits for owner must be unset and read bit must be set.

        Returns:
            bool: True if owner can only read the file.
        """
        return 'r--' == self.perms_owner

    def group_can_only_read(self):
        """
        Checks if group has read-only permissions for the file.
        Therefore, write and execute bits for group must be unset and read bit must be set.

        Returns:
            bool: True if group can only read the file.
        """
        return 'r--' == self.perms_group

    def others_can_only_read(self):
        """
        Checks if 'others' has read-only permissions for the file.
        Therefore, write and execute bits for 'others' must be unset and read bit must be set.
        ('others' in the sense of unix permissions that know about user, group, others.)

        Returns:
            bool: True if 'others' can only read the file.
        """
        return 'r--' == self.perms_other

    def owner_can_write(self):
        """
        Checks if owner can write the file. Read and execute bits are not evaluated.

        Returns:
            bool: True if owner can write the file.
        """
        return 'w' in self.perms_owner

    def group_can_write(self):
        """
        Checks if group can write the file. Read and execute bits are not evaluated.

        Returns:
            bool: True if group can write the file.
        """
        return 'w' in self.perms_group

    def others_can_write(self):
        """
        Checks if 'others' can write the file. Read and execute bits are not evaluated. ('others' in
        the sense of unix permissions that know about user, group, others.)

        Returns:
            bool: True if 'others' can write the file.
        """
        return 'w' in self.perms_other

    def only_root_can_read(self, root_group_can_read=True):
        """
        Checks if only root is allowed to read the file (and anyone else is
        forbidden from reading). Write and execute bits are not checked. The
        read bits for root user/group are not checked because root can
        read/write anything regardless of the read/write permissions.

        When called with ``root_group_can_read`` = ``True``:

        * owner must be root
        * and 'others' permissions must not contain read
        * and if group owner is not root, the 'group' permissions must not
          contain read

        Valid cases::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            ???-??-??    root    nonroot
            ??????-??    root    root
            r--r-----    root    root
            r--------    root    nonroot
            rwxrwx---    root    root
            rwxrwx-wx    root    root

        Specifically, these cases are NOT valid because the owner can chmod
        permissions and grant themselves permissions without root's
        knowledge::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            -??-??-??    nonroot nonroot
            -??r??-??    nonroot root
            ---------    nonroot nonroot

        When called with ``root_group_can_read`` = ``False``:

        * owner must be root
        * and 'group' and 'others' permissions must not contain read

        Valid cases::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            ???-??-??    root    ?
            r--------    root    root
            r--------    root    nonroot
            rwx-wx---    root    root
            rwx-wx---    root    nonroot
            rwx-wxrwx    root    nonroot

        Specifically, these cases are NOT valid because the owner can chmod
        permissions and grant themselves permissions without root's
        knowledge::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            -??-??-??    nonroot nonroot
            ---------    nonroot nonroot

        Args:
            root_group_can_read (bool): if set to True, this tests whether the
            'root' group can also read the file.

        Returns:
            bool: True if only root user (or optionally root group) can read
            the file.
        """

        requirements = True  # The final answer is progressively assembled in this variable.
        requirements &= self.owner == 'root'
        requirements &= not self.others_can_read()
        if root_group_can_read:
            if self.group != 'root':
                # if group is not root, group must not be able to read
                requirements &= not self.group_can_read()
        else:  # root_group_can_read == False
            requirements &= not self.group_can_read()
        return requirements

    def only_root_can_write(self, root_group_can_write=True):
        """
        Checks if only root is allowed to write the file (and anyone else is
        barred from writing). Read and execute bits are not checked. The
        write bits for root user/group are not checked because root can
        read/write anything regardless of the read/write permissions.

        When called with ``root_group_can_write`` = ``True``:

        * owner must be root
        * and 'others' permissions must not contain write
        * and if group owner is not root, the 'group' permissions must not contain write

        Valid cases::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            ????-??-?    root    nonroot
            ???????-?    root    root
            -w--w----    root    root
            -w-------    root    root
            rwxrwx---    root    root
            rwxrwxr-x    root    root

        Specifically, these cases are NOT valid because the owner can chmod
        permissions and grant themselves permissions without root's
        knowledge::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            ?-??-??-?    nonroot nonroot
            ?-??w??-?    nonroot root
            ---------    nonroot nonroot

        When called with ``root_group_can_write`` = ``False``:

        * owner must be root
        * and 'group' and 'others' permissions must not contain write

        Valid cases::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            ????-??-?    root    ?
            -w-------    root    root
            -w-------    root    nonroot
            rwxr-x---    root    root
            rwxr-x---    root    nonroot
            rwxr-xr-x    root    nonroot

        Specifically, these cases are NOT valid because the owner can chmod
        permissions and grant themselves permissions without root's
        knowledge::

            rwxrwxrwx    owner   ownergroup
            -------------------------------
            ?-??-??-?    nonroot nonroot
            ---------    nonroot nonroot

        Args:
            root_group_can_write (bool): if set to True, this tests whether
            'root' group can also write to the file.

        Returns:
            bool: True if only root user (or optionally root group) can write
            the file.
        """

        requirements = True  # The final answer is progressively assembled in this variable.
        requirements &= self.owner == 'root'
        requirements &= not self.others_can_write()
        if root_group_can_write:
            if self.group != 'root':
                # if group is not root, group must not be able to write
                requirements &= not self.group_can_write()
        else:  # root_group_can_write == False
            requirements &= not self.group_can_write()
        return requirements

    def all_zero(self):
        """
        Checks that all permissions are zero ('---------' in ls -l) - nobody but root can read,
        write, exec.

        Returns:
            bool: True if all permissions are zero ('---------')
        """
        _PERM_NOTHING = '---'
        return all(
            (
                self.perms_owner == _PERM_NOTHING,
                self.perms_group == _PERM_NOTHING,
                self.perms_other == _PERM_NOTHING,
            )
        )

    def __repr__(self):
        return 'FilePermissions(' + self.path + ')'
