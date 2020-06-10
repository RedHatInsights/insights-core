"""
CephVersion - command ``ceph -v``
=================================

This module provides plugins access to the Ceph version information gathered from
the ``ceph -v`` command. This module parses the community version to the Red Hat
release version.

The Red Hat Ceph Storage releases and corresponding Ceph package releases are
documented in https://access.redhat.com/solutions/2045583

"""

import re
from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs
from insights.util import deprecated

# TODO: the following metrics need update timely per:
# - https://access.redhat.com/solutions/2045583
# - https://access.redhat.com/articles/1372203
community_to_release_map = {
    "0.80.8-5": {'version': "1.2.3", 'major': '1.2', 'minor': '3', 'downstream_release': 'NA'},
    "0.94.1-15": {'version': "1.3", 'major': '1.3', 'minor': '0', 'downstream_release': 'NA'},
    "0.94.3-3": {'version': "1.3.1", 'major': '1.3', 'minor': '1', 'downstream_release': 'NA'},
    "0.94.5-9": {'version': "1.3.2", 'major': '1.3', 'minor': '2', 'downstream_release': 'NA'},
    "0.94.5-12": {'version': "1.3.2", 'major': '1.3', 'minor': '2', 'downstream_release': 'async'},
    "0.94.5-13": {'version': "1.3.2", 'major': '1.3', 'minor': '2', 'downstream_release': 'async'},
    "0.94.5-14": {'version': "1.3.2", 'major': '1.3', 'minor': '2', 'downstream_release': 'async'},
    "0.94.5-15": {'version': "1.3.2", 'major': '1.3', 'minor': '2', 'downstream_release': 'async'},
    "0.94.9-3": {'version': "1.3.3", 'major': '1.3', 'minor': '3', 'downstream_release': 'NA'},
    "0.94.9-8": {'version': "1.3.3", 'major': '1.3', 'minor': '3', 'downstream_release': 'async'},
    "0.94.9-9": {'version': "1.3.3", 'major': '1.3', 'minor': '3', 'downstream_release': 'async 2'},
    "0.94.10-2": {'version': "1.3.4", 'major': '1.3', 'minor': '4', 'downstream_release': 'NA'},
    "10.2.2-38": {'version': "2.0", 'major': '2', 'minor': '0', 'downstream_release': '0'},
    "10.2.2-41": {'version': "2.0", 'major': '2', 'minor': '0', 'downstream_release': 'async'},
    "10.2.3-13": {'version': "2.1", 'major': '2', 'minor': '1', 'downstream_release': '0'},
    "10.2.3-17": {'version': "2.1", 'major': '2', 'minor': '1', 'downstream_release': 'async'},
    "10.2.5-37": {'version': "2.2", 'major': '2', 'minor': '2', 'downstream_release': '0'},
    "10.2.7-27": {'version': "2.3", 'major': '2', 'minor': '3', 'downstream_release': '0'},
    "10.2.7-28": {'version': "2.3", 'major': '2', 'minor': '3', 'downstream_release': 'async'},
    "10.2.7-32": {'version': "2.4", 'major': '2', 'minor': '4', 'downstream_release': '0'},
    "10.2.7-48": {'version': "2.4", 'major': '2', 'minor': '4', 'downstream_release': 'async'},
    "10.2.10-16": {'version': "2.5", 'major': '2', 'minor': '5', 'downstream_release': '0'},
    "10.2.10-17": {'version': "2.5", 'major': '2', 'minor': '5', 'downstream_release': 'async'},
    "10.2.10-28": {'version': "2.5.1", 'major': '2', 'minor': '5', 'downstream_release': '1'},
    "10.2.10-40": {'version': "2.5.2", 'major': '2', 'minor': '5', 'downstream_release': '2'},
    "10.2.10-43": {'version': "2.5.3", 'major': '2', 'minor': '5', 'downstream_release': '3'},
    "10.2.10-49": {'version': "2.5.4", 'major': '2', 'minor': '5', 'downstream_release': '4'},
    "10.2.10-51": {'version': "2.5.5", 'major': '2', 'minor': '5', 'downstream_release': '5', 'els': True},
    "12.2.1-40": {'version': "3.0", 'major': '3', 'minor': '0', 'downstream_release': '0'},
    "12.2.1-45": {'version': "3.0", 'major': '3', 'minor': '0', 'downstream_release': '1'},
    "12.2.1-46": {'version': "3.0", 'major': '3', 'minor': '0', 'downstream_release': '1 CVE'},
    "12.2.4-6": {'version': "3.0.2", 'major': '3', 'minor': '0', 'downstream_release': '2'},
    "12.2.4-10": {'version': "3.0.3", 'major': '3', 'minor': '0', 'downstream_release': '3'},
    "12.2.4-30": {'version': "3.0.4", 'major': '3', 'minor': '0', 'downstream_release': '4'},
    "12.2.4-42": {'version': "3.0.5", 'major': '3', 'minor': '0', 'downstream_release': '5'},
    "12.2.5-42": {'version': "3.1", 'major': '3', 'minor': '1', 'downstream_release': '0'},
    "12.2.5-59": {'version': "3.1.1", 'major': '3', 'minor': '1', 'downstream_release': '1'},
    "12.2.8-52": {'version': "3.2", 'major': '3', 'minor': '2', 'downstream_release': '0'},
    "12.2.8-89": {'version': "3.2.1", 'major': '3', 'minor': '2', 'downstream_release': '1'},
    "12.2.8-128": {'version': "3.2.2", 'major': '3', 'minor': '2', 'downstream_release': '2'},
    "12.2.12-45": {'version': "3.3", 'major': '3', 'minor': '3', 'downstream_release': '0'},
    "12.2.12-48": {'version': "3.3", 'major': '3', 'minor': '3', 'downstream_release': 'async'},
    "12.2.12-74": {'version': "3.3.1", 'major': '3', 'minor': '3', 'downstream_release': '1'},
    "12.2.12-79": {'version': "3.3.1", 'major': '3', 'minor': '3', 'downstream_release': 'async'},
    "12.2.12-84": {'version': "3.3.2", 'major': '3', 'minor': '3', 'downstream_release': '2'},
    "12.2.12-101": {'version': "3.3.4", 'major': '3', 'minor': '3', 'downstream_release': '4'},
    "14.2.4-125": {'version': "4.0", 'major': '4', 'minor': '0', 'downstream_release': '0'},
    "14.2.8-59": {'version': "4.1", 'major': '4', 'minor': '1', 'downstream_release': '0'},
}


@parser(Specs.ceph_v)
class CephVersion(CommandParser):
    """
    Class for parsing the output of command ``ceph -v``.

    Typical output of the ``ceph -v`` command is::

        ceph version 0.94.9-9.el7cp (b83334e01379f267fb2f9ce729d74a0a8fa1e92c)

    Attributes:
        version (str): The Red Hat release version
        major (str): The major version of Red Hat release version
        minor (str): The minor version of Red Hat release version
        is_els (boolean): If the verion in 'Extended life cycle support (ELS) add-on' phase
        downstream_release (str): The downstream release info
        upstream_version (dict): The detailed upstream version info with the
            following keys `release (int)`, `major (int)` and `minor (int)`.

    Example:
        >>> ceph_v.version
        '1.3.3'
        >>> ceph_v.major
        '1.3'
        >>> ceph_v.minor
        '3'
        >>> ceph_v.is_els
        False
    """

    def parse_content(self, content):
        # Parse Ceph Version Content and get Release, Major, Minor number
        if not content:
            raise SkipException("Empty Ceph Version Line", content)

        ceph_version_line = content[-1]
        # re search pattern
        pattern_community = r'((\d{1,2})\.(\d{1,2})\.((\d{1,2})|x))((\-(\d+)))'
        community_version_mo = re.search(pattern_community, str(ceph_version_line), 0)
        if not community_version_mo:
            raise SkipException("Wrong Format Ceph Version", content)

        community_version = community_version_mo.group(0)
        release_data = community_to_release_map.get(community_version, None)
        if not release_data:
            raise SkipException("No Mapping Release Version. Ceph Release Number is Null", content)

        self.version = release_data['version']
        self.major = release_data['major']
        self.minor = release_data['minor']
        self.is_els = release_data.get('els', False)
        self.downstream_release = release_data['downstream_release']
        self.upstream_version = {
            "release": int(community_version_mo.group(2)),
            "major": int(community_version_mo.group(3)),
            "minor": int(community_version_mo.group(4))
        }


class CephVersionError(Exception):
    """
    .. note::
        This class is deprecated, please use :py:class:`insights.parsers.SkipException` instead.
    """

    def __init__(self, *args, **kwargs):
        deprecated(CephVersionError, "Use SkipException instead.")
        super(CephVersionError, self).__init__(*args, **kwargs)
