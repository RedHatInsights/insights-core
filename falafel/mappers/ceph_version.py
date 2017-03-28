"""
CephVersion - ``ceph -v`` command output
===================================

The ``CephVersion`` class reads the output of the ``ceph -v`` command and
interprets it.  Deriving the Red Hat deriving
the RHEL release from the kernel version.

Note:
    This module can only be used for Ceph.

An example from the following ``ceph -v`` output::

    ceph version 0.94.9-9.el7cp (b83334e01379f267fb2f9ce729d74a0a8fa1e92c)

Example:
    >>> ceph_ver = shared[CephVersion]
    >>> ceph_ver.major
    '1.3'

"""

from .. import Mapper, mapper

community_to_release_map = {
    "0.94": "1.3",
    "10.2": "2.0",
}

release_to_community_map = {v: k for k, v in community_to_release_map.items()}


class CephVersionError(Exception):
    """
    Exception subclass for errors related to the content data and the
    CephVersion class.

    This exception should not be caught by rules plugins unless it is necessary
    for the plugin to return a particular answer when a problem occurs with
    ceph version data.  If a plugin catches this exception it must reraise it so that
    the engine has the opportunity to handle it/log it as necessary.
    """

    def __init__(self, message, errors):
        """Class constructor"""

        super(CephVersionError, self).__init__(message)
        self.errors = errors
        self.message = message

class CephVersion(Mapper):
    """ Class for parsing the content of ``ceph_version``."""

    def parse_content(self, content):
        # Parse Ceph Version Content and get the Major number

        if not content:
            raise CephVersionError("Empty Ceph Version Line",content)

        ceph_version_line = content[-1]
        content_list = ceph_version_line.split()

        if len(content_list) < 3:
            raise CephVersionError("Error Ceph Version Line", ceph_version_line)

        # I will change this to get detail version infomation


        full_version = content_list[2]
        full_version_list = full_version.split(".")

        if len(full_version_list) < 2:
            raise CephVersionError("Error Ceph Version Number",ceph_version_line)
        self.major_number = None
        major_list = [full_version_list[0], full_version_list[1]]
        community_major_number = ".".join(major_list)
        if community_major_number in community_to_release_map.keys() :
            self.major_number = community_to_release_map[community_major_number]

    @property
    def major(self):
        if self.major_number:
            return self.major_number
        else:
            return ""


