import re


class FilePermissions(object):
    """
    Class for parsing `ls -l` line targeted at concrete file and handling parsed properties.

    It is useful for checking file permissions and owner.

    Attributes:
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

    _PERMISSIONS_PATTERN = re.compile('''
        ^
        .([-rwxsS]{3})([-rwxsS]{3})([-rwxsS]{3})   # -rwxrwxrwx
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        # ^^^^^^^^^^
        # Valid characters are -rwxsS
        #   s == execute bit and sticky bit
        #   S == sticky bit without execute bit

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

        \s+\S+\s+                # size and spaces around
        # -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
        #                        ^^^^^^

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
        ''', re.VERBOSE)

    def __init__(self, line):
        """
        Args:
            line (str): A line from `ls -l /concrete/file` execution. Such as:
                        -rw-------. 1 root root 762 Sep 23 002 /etc/ssh/sshd_config
                        -rw-------. 1 root root 4308 Apr 22 15:57 /etc/ssh/sshd_config
                        -rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub2/grub.cfg
        Raises:
            ValueError: If line is malformed
        """
        self.line = line
        r = self._PERMISSIONS_PATTERN.search(self.line)
        if r:
            (self.perms_owner, self.perms_group, self.perms_other,
             self.owner, self.group, self.path) = r.groups()
        else:
            raise ValueError('Invalid `ls -l` line "{}"'.format(self.line))

    @classmethod
    def from_dict(self, dirent):
        """
        Create a new FilePermissions object from the given dictionary.  This
        works with the FileListing parser class, which has already done the
        hard work of pulling many of these fields out.  We create an object
        with all the dictionary keys available as properties, and also split
        the ``perms`` string up into owner, group
        """
        # Check that we have at least as much data as the __init__ requires
        for k in ['perms', 'owner', 'group', 'name', 'dir']:
            if k not in dirent:
                raise ValueError("Need required key '{k}'".format(k=k))
        # Copy all values across
        for k in dirent:
            setattr(self, k, dirent[k])
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
        return all((
            self.perms_owner == _PERM_NOTHING,
            self.perms_group == _PERM_NOTHING,
            self.perms_other == _PERM_NOTHING,
        ))

    def __repr__(self):
        return 'FilePermissions(' + self.path + ')'
