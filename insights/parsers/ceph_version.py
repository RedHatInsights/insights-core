"""
CephVersion - command ``/usr/bin/ceph -v``
==========================================

This module provides plugins access to the Ceph version information gathered from
the ``ceph -v`` command. This module parses the community version to the Red Hat
release version.

The Red Hat Ceph Storage releases and corresponding Ceph package releases are
documented in https://access.redhat.com/solutions/2045583

Typical output of the ``ceph -v`` command is::

    ceph version 0.94.9-9.el7cp (b83334e01379f267fb2f9ce729d74a0a8fa1e92c)

Note:
    This module can only be used for Ceph.

Example:
    >>> ceph_ver = shared[CephVersion]
    >>> ceph_ver.version
    '1.3.3'
    >>> ceph_ver.major
    '1.3'
    >>> ceph_ver.minor
    '3'
"""

from .. import parser, CommandParser
import re
from insights.specs import Specs

community_to_release_map = {
    "0.94.1-15": {'version': "1.3.0", 'major': '1.3', 'minor': '0', 'downstream_release': 'NA'},
    "0.94.3-3": {'version': "1.3.1", 'major': '1.3', 'minor': '1', 'downstream_release': 'NA'},
    "0.94.5-9": {'version': "1.3.2", 'major': '1.3', 'minor': '2', 'downstream_release': 'NA'},
    "0.94.9-3": {'version': "1.3.3", 'major': '1.3', 'minor': '3', 'downstream_release': 'NA'},
    "0.94.9-9": {'version': "1.3.3", 'major': '1.3', 'minor': '3', 'downstream_release': 'async 2'},
    "0.94.10-2": {'version': "1.3.4", 'major': '1.3', 'minor': '4', 'downstream_release': 'NA'},
    "10.2.2-38": {'version': "2.0", 'major': '2', 'minor': '0', 'downstream_release': '0'},
    "10.2.3-13": {'version': "2.1", 'major': '2', 'minor': '1', 'downstream_release': '0'},
    "10.2.5": {'version': "2.2", 'major': '2', 'minor': '2', 'downstream_release': '0'},
    "10.2.5-37": {'version': "2.2", 'major': '2', 'minor': '2', 'downstream_release': '0'},
    "10.2.7-27": {'version': "2.3", 'major': '2', 'minor': '3', 'downstream_release': '0'},
    "10.2.7-28": {'version': "2.3", 'major': '2', 'minor': '3', 'downstream_release': 'async'},
    "10.2.7-48": {'version': "2.4", 'major': '2', 'minor': '4', 'downstream_release': 'async'},
    "10.2.10-16": {'version': "2.5", 'major': '2', 'minor': '5', 'downstream_release': '0'},
    "10.2.10-28": {'version': "2.5.1", 'major': '2', 'minor': '5', 'downstream_release': '1'},
    "10.2.10-40": {'version': "2.5.2", 'major': '2', 'minor': '5', 'downstream_release': '2'},
    "10.2.10-43": {'version': "2.5.3", 'major': '2', 'minor': '5', 'downstream_release': '3'},
    "12.2.4-6": {'version': "3.0.2", 'major': '3', 'minor': '0', 'downstream_release': '2'},
    "12.2.4-10": {'version': "3.0.3", 'major': '3', 'minor': '0', 'downstream_release': '3'},
    "12.2.4-30": {'version': "3.0.4", 'major': '3', 'minor': '0', 'downstream_release': '4'},
    "12.2.4-42": {'version': "3.0.5", 'major': '3', 'minor': '0', 'downstream_release': '5'},
    "12.2.5-42": {'version': "3.1", 'major': '3', 'minor': '1', 'downstream_release': '0'},
    "12.2.5-59": {'version': "3.1.1", 'major': '3', 'minor': '1', 'downstream_release': '1'},
    "12.2.8-52": {'version': "3.2", 'major': '3', 'minor': '2', 'downstream_release': '0'},
    "12.2.8-89": {'version': "3.2.1", 'major': '3', 'minor': '2', 'downstream_release': '1'}
}


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


@parser(Specs.ceph_v)
class CephVersion(CommandParser):
    """ Class for parsing the content of ``ceph_version``."""

    def parse_content(self, content):
        # Parse Ceph Version Content and get Release, Major, Minor number
        if not content:
            raise CephVersionError("Empty Ceph Version Line", content)

        ceph_version_line = content[-1]
        # re search pattern
        pattern_community = r'((\d{1,2})\.(\d{1,2})\.((\d{1,2})|x))((\-(\d{1,2}))?)'
        community_version_mo = re.search(pattern_community, str(ceph_version_line), 0)
        if not community_version_mo:
            raise CephVersionError("Wrong Format Ceph Version", content)

        community_version = community_version_mo.group(0)
        release_data = community_to_release_map.get(community_version, None)
        if not release_data:
            raise CephVersionError("No Mapping Release Version. Ceph Release Number is Null", content)

        self.version = release_data['version']
        self.major = release_data['major']
        self.minor = release_data['minor']
        self.downstream_release = release_data['downstream_release']
